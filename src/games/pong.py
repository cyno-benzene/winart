import random
from typing import List, Tuple
from .base import Game
from src.wrapper.winart import EngineEvent, KEY_DOWN, KEY_UP
from src.animation.sprite import PixelSprite, PixelFrame
from src.animation.animator import Animator

# Key codes
VK_W = 0x57
VK_S = 0x53
VK_UP = 0x26
VK_DOWN = 0x28

class PongGame(Game):
    def __init__(self):
        super().__init__("Pong")
        self.paddle_width = 20
        self.paddle_height = 100
        self.ball_size = 15
        self.screen_width = 1920
        self.screen_height = 1080
        self.paddle1_y = self.screen_height // 2 - 50
        self.paddle2_y = self.screen_height // 2 - 50
        self.ball_pos = [self.screen_width // 2, self.screen_height // 2]
        self.ball_vel = [400, 400]
        self.keys_pressed = set()
        
        # Frames
        self.paddle_frame = PixelFrame([(x, y, 255, 255, 255) for x in range(20) for y in range(100)])
        self.ball_frame = PixelFrame([(x, y, 255, 255, 255) for x in range(15) for y in range(15)])

    def on_init(self, animator: Animator):
        self.paddle1_y = self.screen_height // 2 - 50
        self.paddle2_y = self.screen_height // 2 - 50
        self.ball_pos = [self.screen_width // 2, self.screen_height // 2]
        self.ball_vel = [400, 400]
        self.score = 0
        animator.sprites.clear()
        self._sync_sprites(animator)

    def on_event(self, event: EngineEvent, animator: Animator):
        if event.type == KEY_DOWN:
            self.keys_pressed.add(event.button)
        elif event.type == KEY_UP:
            if event.button in self.keys_pressed:
                self.keys_pressed.remove(event.button)

    def on_update(self, dt: float, animator: Animator):
        # Paddle 1 (AI)
        target_y = self.ball_pos[1] - self.paddle_height // 2
        dy = target_y - self.paddle1_y
        self.paddle1_y += dy * dt * 5.0 # Smooth AI movement
        
        # Paddle 2 (Player)
        if VK_UP in self.keys_pressed:
            self.paddle2_y -= 600 * dt
        if VK_DOWN in self.keys_pressed:
            self.paddle2_y += 600 * dt
            
        # Clamp paddles
        self.paddle1_y = max(0, min(self.screen_height - self.paddle_height, self.paddle1_y))
        self.paddle2_y = max(0, min(self.screen_height - self.paddle_height, self.paddle2_y))
        
        # Ball physics
        self.ball_pos[0] += self.ball_vel[0] * dt
        self.ball_pos[1] += self.ball_vel[1] * dt
        
        # Wall bounce
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.screen_height - self.ball_size:
            self.ball_vel[1] *= -1
            
        # Paddle bounce
        if self.ball_pos[0] <= 40 and self.paddle1_y <= self.ball_pos[1] <= self.paddle1_y + self.paddle_height:
            self.ball_vel[0] = abs(self.ball_vel[0]) * 1.05
        if self.ball_pos[0] >= self.screen_width - 60 and self.paddle2_y <= self.ball_pos[1] <= self.paddle2_y + self.paddle_height:
            self.ball_vel[0] = -abs(self.ball_vel[0]) * 1.05
            
        # Score
        if self.ball_pos[0] < 0:
            self.ball_pos = [self.screen_width // 2, self.screen_height // 2]
            self.ball_vel = [400, 400]
        elif self.ball_pos[0] > self.screen_width:
            self.ball_pos = [self.screen_width // 2, self.screen_height // 2]
            self.ball_vel = [-400, 400]
            self.score += 1
            
        self._sync_sprites(animator)

    def _sync_sprites(self, animator: Animator):
        scale = 1.0 / animator.pixel_size # Because frames are in actual pixels
        
        if "paddle1" not in animator.sprites:
            animator.add_sprite("paddle1", PixelSprite(self.paddle_frame, 20, self.paddle1_y, scale=scale))
        else:
            animator.sprites["paddle1"].y = self.paddle1_y
            
        if "paddle2" not in animator.sprites:
            animator.add_sprite("paddle2", PixelSprite(self.paddle_frame, self.screen_width - 40, self.paddle2_y, scale=scale))
        else:
            animator.sprites["paddle2"].y = self.paddle2_y
            
        if "ball" not in animator.sprites:
            animator.add_sprite("ball", PixelSprite(self.ball_frame, self.ball_pos[0], self.ball_pos[1], scale=scale))
        else:
            animator.sprites["ball"].x = self.ball_pos[0]
            animator.sprites["ball"].y = self.ball_pos[1]
