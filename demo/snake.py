import os
import math
import random
import time
from src.animation import (
    Animator, SpriteSheetLoader, PixelFrame, SegmentedSprite, DraggableSegmentedSprite
)

# Configuration
PIXEL_SIZE = 8
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

def create_snake_assets():
    # Create simple colored blocks for head and body
    head_frame = PixelFrame()
    # 4x4 head block
    for y in range(4):
        for x in range(4):
            head_frame.pixels.append((x, y, 0, 255, 0)) # Green head
            
    body_frame = PixelFrame()
    # 4x4 body block
    for y in range(4):
        for x in range(4):
            body_frame.pixels.append((x, y, 0, 200, 0)) # Lighter green body
            
    return [head_frame, body_frame]

def main():
    print("Initializing Nokia Snake Demo...")
    
    # 1. Setup Animator
    animator = Animator(pool_size=1024)
    animator.engine.set_transparency(True)
    
    # 2. Create Assets
    head_frame, body_frame = create_snake_assets()
    
    # 3. Create Snake
    # A segmented sprite with 20 segments
    snake = DraggableSegmentedSprite(
        segment_frames=[head_frame, body_frame],
        segment_count=20,
        spacing=15.0,
        x=SCREEN_WIDTH // 2,
        y=SCREEN_HEIGHT // 2,
        scale=2.0
    )
    animator.add_sprite("snake", snake)
    
    # 4. AI Behavior: Slithering
    class SnakeAI:
        def __init__(self, snake):
            self.snake = snake
            self.angle = 0.0
            self.speed = 200.0
            self.turn_speed = 2.0
            self.target_angle = 0.0
            self.change_timer = 0.0
            
        def update(self, dt):
            if self.snake.dragging:
                # If dragging, don't move automatically
                # But we can update the angle to face the move direction
                return

            self.change_timer -= dt
            if self.change_timer <= 0:
                self.target_angle = random.uniform(0, 2 * math.pi)
                self.change_timer = random.uniform(1.0, 3.0)
                
            # Smoothly turn towards target
            da = self.target_angle - self.angle
            while da > math.pi: da -= 2 * math.pi
            while da < -math.pi: da += 2 * math.pi
            
            self.angle += da * self.turn_speed * dt
            
            # Move in current angle
            self.snake.x += math.cos(self.angle) * self.speed * dt
            self.snake.y += math.sin(self.angle) * self.speed * dt
            
            # Screen wrap
            if self.snake.x < 0: self.snake.x = SCREEN_WIDTH
            if self.snake.x > SCREEN_WIDTH: self.snake.x = 0
            if self.snake.y < 0: self.snake.y = SCREEN_HEIGHT
            if self.snake.y > SCREEN_HEIGHT: self.snake.y = 0

    ai = SnakeAI(snake)
    
    # Wrap update
    original_update = snake.update
    def custom_update(dt):
        ai.update(dt)
        original_update(dt)
    snake.update = custom_update
    
    print("Snake is alive! Drag its head to move it, or let it slither.")
    print("Press Ctrl+C to stop.")
    
    animator.run()

if __name__ == "__main__":
    main()
