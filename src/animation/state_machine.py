from typing import Dict, List, Optional, Callable
from .sprite import AnimatedSprite, PixelFrame

class AnimationState:
    def __init__(self, name: str, frames: List[PixelFrame], fps: float = 8.0, loop: bool = True):
        self.name = name
        self.frames = frames
        self.fps = fps
        self.loop = loop

class AnimationStateMachine:
    """
    Manages states for an AnimatedSprite, allowing for transitions 
    between different animation sequences.
    """
    def __init__(self, sprite: AnimatedSprite):
        self.sprite = sprite
        self.states: Dict[str, AnimationState] = {}
        self.current_state: Optional[AnimationState] = None
        self.on_state_complete: Optional[Callable[[str], None]] = None

    def add_state(self, name: str, frames: List[PixelFrame], fps: float = 8.0, loop: bool = True):
        self.states[name] = AnimationState(name, frames, fps, loop)

    def set_state(self, name: str, restart: bool = False):
        if name not in self.states:
            return
        
        new_state = self.states[name]
        if self.current_state == new_state and not restart:
            return
            
        self.current_state = new_state
        self.sprite.frames = new_state.frames
        self.sprite.fps = new_state.fps
        self.sprite.current_frame_idx = 0
        self.sprite.time_accum = 0.0
        self.sprite.playing = True

    def update(self, dt: float):
        """
        Updates the state machine. Should be called after sprite.update(dt).
        Handles non-looping state completions.
        """
        if not self.current_state or self.current_state.loop:
            return
            
        # Check if we've completed the non-looping animation
        if self.sprite.current_frame_idx == len(self.current_state.frames) - 1:
            frame_duration = 1.0 / self.current_state.fps
            if self.sprite.time_accum >= frame_duration:
                # Stay on last frame but stop playing
                self.sprite.playing = False
                if self.on_state_complete:
                    self.on_state_complete(self.current_state.name)
