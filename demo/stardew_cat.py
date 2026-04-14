import os
import random
import argparse
from src.animation import (
    Animator, SpriteSheetLoader, DraggableSprite,
    AnimationStateMachine, PixelFrame
)

# Configuration
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

def main():
    parser = argparse.ArgumentParser(description="Stardew Valley Cat Desktop Companion")
    parser.add_argument("--sheet", type=str, default="demo/assets/stardew_valley_cat.png", help="Path to sprite sheet")
    parser.add_argument("--width", type=int, default=32, help="Frame width")
    parser.add_argument("--height", type=int, default=32, help="Frame height")
    parser.add_argument("--colors", type=int, default=0, help="Quantize colors (0 to disable)")
    parser.add_argument("--pool", type=int, default=1024, help="Window pool size")
    parser.add_argument("--scale", type=float, default=3.0, help="Scale multiplier for sprite")
    parser.add_argument("--pixel-size", type=int, default=8, help="Physical size of one window pixel")
    parser.add_argument("--debug", action="store_true", help="Enable debug bounding box")
    args = parser.parse_args()

    print(f"Initializing Stardew Cat with pool size {args.pool}...")
    
    # 1. Setup Animator
    animator = Animator(pool_size=args.pool, pixel_size=args.pixel_size)
    animator.engine.set_transparency(True)
    
    # 2. Load Assets
    if not os.path.exists(args.sheet):
        print(f"Asset not found: {args.sheet}")
        return
        
    print(f"Loading sheet: {args.sheet} (Quantizing to {args.colors} colors)")
    all_frames = SpriteSheetLoader.load_sheet(
        args.sheet, 
        args.width, 
        args.height, 
        quantize_colors=args.colors,
        auto_scale_to_pool=args.pool
    )
    
    if not all_frames:
        print("Failed to load any frames!")
        return

    print(f"Loaded {len(all_frames)} frames.")

    # Animation mappings for Stardew Cat
    idle_frames = all_frames[0:4] if len(all_frames) >= 4 else [all_frames[0]]
    walk_frames = all_frames[4:8] if len(all_frames) >= 8 else all_frames
    sit_frames = [all_frames[12]] if len(all_frames) >= 13 else [all_frames[0]]
    
    # 3. Create Cat
    cat = DraggableSprite(idle_frames, fps=4, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 200, scale=args.scale)
    cat.debug_box = args.debug
    cat.ensure_visible(SCREEN_WIDTH, SCREEN_HEIGHT, pixel_size=args.pixel_size)
    animator.add_sprite("cat", cat)
    
    # 4. Setup State Machine
    sm = AnimationStateMachine(cat)
    sm.add_state("idle", idle_frames, fps=4, loop=True)
    sm.add_state("walk", walk_frames, fps=8, loop=True)
    sm.add_state("sit", sit_frames, loop=True)
    sm.set_state("idle")
    
    # 5. AI Behavior
    class CatAI:
        def __init__(self, cat, sm):
            self.cat = cat
            self.sm = sm
            self.state = "idle"
            self.timer = 0
            self.target_x = cat.x
            self.speed = 100
            
        def update(self, dt):
            self.timer -= dt
            self.sm.update(dt)
            
            # Ensure visible every frame
            self.cat.ensure_visible(SCREEN_WIDTH, SCREEN_HEIGHT, pixel_size=args.pixel_size)

            if self.cat.dragging:
                self.sm.set_state("walk")
                return

            if self.timer <= 0:
                r = random.random()
                if r < 0.3:
                    self.state = "idle"
                    self.sm.set_state("idle")
                    self.timer = random.uniform(2, 5)
                elif r < 0.6:
                    self.state = "walk"
                    self.sm.set_state("walk")
                    self.target_x = random.randint(100, SCREEN_WIDTH - 100)
                    self.timer = abs(self.target_x - self.cat.x) / self.speed
                else:
                    self.state = "sit"
                    self.sm.set_state("sit")
                    self.timer = random.uniform(3, 10)
            
            if self.state == "walk":
                dx = self.target_x - self.cat.x
                if abs(dx) > 5:
                    step = self.speed * dt * (1 if dx > 0 else -1)
                    self.cat.x += step
                else:
                    self.timer = 0
                    
    ai = CatAI(cat, sm)
    
    # Hook update
    original_update = cat.update
    def custom_update(dt):
        ai.update(dt)
        original_update(dt)
    cat.update = custom_update
    
    print("Cat is running! Drag it with your mouse.")
    print("Press Ctrl+C to exit.")
    animator.run()

if __name__ == "__main__":
    main()
