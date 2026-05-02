import time
from typing import Dict, Optional, Type
from .base import Game
from src.animation.animator import Animator

class GameManager:
    """
    Manages loading, switching, and running games within the Animator.
    """
    def __init__(self, animator: Animator):
        self.animator = animator
        self.games: Dict[str, Game] = {}
        self.current_game: Optional[Game] = None
        self._last_time = time.perf_counter()

    def register_game(self, game: Game):
        self.games[game.name] = game

    def start_game(self, name: str):
        if self.current_game:
            self.current_game.on_stop(self.animator)
            
        if name in self.games:
            self.current_game = self.games[name]
            self.current_game.on_init(self.animator)
            self.current_game.running = True
            print(f"Started game: {name}")

    def stop_game(self):
        if self.current_game:
            self.current_game.on_stop(self.animator)
            self.current_game = None

    def update(self):
        """
        To be called in the main loop or timer.
        """
        now = time.perf_counter()
        dt = now - self._last_time
        self._last_time = now

        if self.current_game and self.current_game.running:
            # Poll events from animator (or directly)
            events = self.animator.engine.poll_events()
            for event in events:
                self.current_game.on_event(event, self.animator)
            
            # Update game logic
            self.current_game.on_update(dt, self.animator)
            
            # Step the animator to update sprites and render
            self.animator.step(dt)
