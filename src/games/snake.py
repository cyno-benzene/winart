import random
from typing import List, Tuple
from .base import Game
from src.wrapper.winart import EngineEvent, KEY_DOWN
from src.animation.sprite import PixelSprite, PixelFrame
from src.animation.animator import Animator

# Key codes
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28

class SnakeGame(Game):
    def __init__(self):
        super().__init__("Snake")
        self.pixel_size = 20
        self.grid_width = 1920 // self.pixel_size
        self.grid_height = 1080 // self.pixel_size
        self.snake: List[Tuple[int, int]] = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (0, 0)
        self.move_timer = 0.0
        self.move_interval = 0.1
        self.game_over = False
        
        # Shared frames
        self.head_frame = PixelFrame([(0, 0, 0, 255, 0)])
        self.body_frame = PixelFrame([(0, 0, 0, 200, 0)])
        self.food_frame = PixelFrame([(0, 0, 255, 0, 0)])

    def on_init(self, animator: Animator):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.move_timer = 0.0
        
        animator.sprites.clear()
        self._sync_sprites(animator)

    def spawn_food(self):
        while True:
            self.food = (random.randint(0, self.grid_width - 1), 
                         random.randint(0, self.grid_height - 1))
            if self.food not in self.snake:
                break

    def on_event(self, event: EngineEvent, animator: Animator):
        if event.type == KEY_DOWN:
            if event.button == VK_UP and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.button == VK_DOWN and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.button == VK_LEFT and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.button == VK_RIGHT and self.direction != (-1, 0):
                self.next_direction = (1, 0)

    def on_update(self, dt: float, animator: Animator):
        if self.game_over:
            return

        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.direction = self.next_direction
            
            # Move head
            head_x, head_y = self.snake[0]
            new_head = (head_x + self.direction[0], head_y + self.direction[1])
            
            # Check collisions
            if (new_head[0] < 0 or new_head[0] >= self.grid_width or
                new_head[1] < 0 or new_head[1] >= self.grid_height or
                new_head in self.snake):
                self.game_over = True
                print(f"Game Over! Score: {self.score}")
                return
            
            self.snake.insert(0, new_head)
            
            # Check food
            if new_head == self.food:
                self.score += 10
                self.spawn_food()
                self.move_interval = max(0.05, 0.1 - (self.score / 1000.0))
            else:
                self.snake.pop()
            
            self._sync_sprites(animator)

    def _sync_sprites(self, animator: Animator):
        # Scale for sprites
        scale = self.pixel_size / animator.pixel_size
        
        # Remove old snake sprites if they exceed current snake length
        current_sprite_keys = [k for k in animator.sprites.keys() if k.startswith("snake_")]
        for k in current_sprite_keys:
            try:
                idx = int(k.split("_")[1])
                if idx >= len(self.snake):
                    del animator.sprites[k]
            except (ValueError, IndexError):
                pass

        # Update or add snake segments
        for i, (x, y) in enumerate(self.snake):
            key = f"snake_{i}"
            frame = self.head_frame if i == 0 else self.body_frame
            if key in animator.sprites:
                s = animator.sprites[key]
                s.x = x * self.pixel_size
                s.y = y * self.pixel_size
            else:
                s = PixelSprite(frame, x * self.pixel_size, y * self.pixel_size, scale=scale)
                animator.add_sprite(key, s)
                
        # Food sprite
        if "food" in animator.sprites:
            s_food = animator.sprites["food"]
            s_food.x = self.food[0] * self.pixel_size
            s_food.y = self.food[1] * self.pixel_size
        else:
            s_food = PixelSprite(self.food_frame, self.food[0] * self.pixel_size, self.food[1] * self.pixel_size, scale=scale)
            animator.add_sprite("food", s_food)
