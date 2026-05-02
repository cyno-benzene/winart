from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from src.wrapper.winart import EngineEvent
from src.animation.animator import Animator

class Game(ABC):
    """
    Base class for all retro games.
    """
    def __init__(self, name: str):
        self.name = name
        self.running = False
        self.score = 0
        self.high_score = 0

    @abstractmethod
    def on_init(self, animator: Animator):
        """Setup assets and initial state."""
        pass

    @abstractmethod
    def on_update(self, dt: float, animator: Animator):
        """Game logic (movement, collision, etc.)."""
        pass

    @abstractmethod
    def on_event(self, event: EngineEvent, animator: Animator):
        """Handle input events (keyboard and mouse)."""
        pass

    def on_stop(self, animator: Animator):
        """Cleanup logic when game is stopped."""
        self.running = False
        # Clear sprites associated with this game
        animator.sprites.clear()
        animator.engine.render([])
