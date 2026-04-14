import numpy as np
from typing import Dict, List
from src.wrapper.winart import WindowEngine, Rect
from .timer import FrameTimer
from .sprite import Sprite

class Animator:
    """
    Manages a collection of sprites and runs the update/render loop.
    Ensures that the engine is used efficiently by batching all sprite updates into 
    single layer render calls.
    """
    def __init__(self, dll_path: str | None = None, pool_size: int = 2000, target_fps: float = 60.0, pixel_size: int = 8):
        if dll_path:
            self.engine = WindowEngine(dll_path, pool_size)
        else:
            self.engine = WindowEngine(pool_size=pool_size)
        self.timer = FrameTimer(target_fps)
        self.pixel_size = pixel_size
        self.sprites: Dict[str, Sprite] = {}
        self.running = False

    def add_sprite(self, name: str, sprite: Sprite):
        self.sprites[name] = sprite
        return sprite

    def get_sprite(self, name: str) -> Sprite:
        return self.sprites.get(name) # type: ignore

    def run(self):
        """
        Main animation loop. This is a blocking call.
        """
        self.running = True
        idle_ticks = 0
        try:
            while self.running:
                dt = self.timer.tick()
                
                # Poll events from engine
                events = self.engine.poll_events()
                has_input = len(events) > 0
                for event in events:
                    # Dispatch to sprites (in reverse order for correct click layering)
                    for sprite in reversed(list(self.sprites.values())):
                        if sprite.visible:
                            if sprite.handle_event(event, pixel_size=self.pixel_size):
                                break # Event consumed
                
                # Update all sprites and check if any are active
                has_activity = has_input
                for sprite in self.sprites.values():
                    sprite.update(dt)
                    # Check if sprite is 'playing' or 'dragging'
                    if getattr(sprite, 'playing', False) or getattr(sprite, 'dragging', False):
                        has_activity = True
                
                # Render loop
                layer_rects: Dict[int, List[np.ndarray]] = {}
                for sprite in self.sprites.values():
                    if sprite.visible:
                        rects = sprite.to_rects(pixel_size=self.pixel_size)
                        if rects.size > 0:
                            layer_id = sprite.layer_id
                            if layer_id not in layer_rects:
                                layer_rects[layer_id] = []
                            layer_rects[layer_id].append(rects)
                
                all_rect_data = []
                for layer_id in sorted(layer_rects.keys()):
                    all_rect_data.extend(layer_rects[layer_id])
                
                if all_rect_data:
                    full_rect_data = np.concatenate(all_rect_data)
                    self.engine.render(full_rect_data)
                else:
                    self.engine.render([])

                # CPU optimization: if no activity for a while, slow down the loop
                if not has_activity:
                    idle_ticks += 1
                    if idle_ticks > 60: # After 1 second of inactivity
                        import time
                        time.sleep(0.05) # Cap at ~20 FPS for idle polling
                else:
                    idle_ticks = 0

        except KeyboardInterrupt:
            self.stop()
        finally:
            self.engine.close()

    def stop(self):
        self.running = False
