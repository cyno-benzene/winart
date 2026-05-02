import pytest
import numpy as np
from src.wrapper.winart import WindowEngine, Rect, EngineEvent, KEY_DOWN
from src.games.snake import SnakeGame
from src.animation.animator import Animator

def test_engine_initialization():
    engine = WindowEngine(pool_size=10)
    assert engine is not None
    engine.close()

def test_snake_game_logic():
    game = SnakeGame()
    animator = Animator(pool_size=100)
    game.on_init(animator)
    
    assert len(game.snake) == 3
    assert game.score == 0
    
    # Simulate a move
    initial_head = game.snake[0]
    game.on_update(0.2, animator) # Trigger a move (interval is 0.1)
    
    assert game.snake[0] != initial_head
    animator.engine.close()

def test_event_polling():
    # This test might be tricky without a real window interaction, 
    # but we can at least check if the function exists and doesn't crash.
    engine = WindowEngine(pool_size=10)
    events = engine.poll_events()
    assert isinstance(events, list)
    engine.close()

def test_animator_step():
    animator = Animator(pool_size=100)
    animator.step(0.016)
    # Should not crash
    animator.engine.close()
