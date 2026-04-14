import os
import random
import time
from src.animation import Animator, SpriteSheetLoader, AnimatedSprite, ease_in_out_quad, lerp

# Configuration
PIXEL_SIZE = 8 # Each pixel in the sprite will be 8x8 pixels
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
CAT_Y = SCREEN_HEIGHT - 300 # Place cat slightly higher to be sure it's visible

def main():
    print("Initializing Animated Cat Avatar...")
    
    # 1. Setup Animator (pool size based on 16x16 sprite max)
    animator = Animator(pool_size=512)
    
    # 2. Enable transparency for the floating effect
    # Windows with WS_EX_LAYERED need this to be visible and clear the background
    animator.engine.set_transparency(True)
    
    # 3. Load Sprite sheet
    assets_path = os.path.join("demo", "assets", "cat_sprite.png")
    if not os.path.exists(assets_path):
        print(f"Assets not found at {assets_path}. Please run demo/generate_assets.py first.")
        return
        
    frames = SpriteSheetLoader.load_sheet(assets_path, 16, 16)
    
    # 3. Create cat sprite
    cat = AnimatedSprite(frames, fps=4, x=SCREEN_WIDTH // 2, y=CAT_Y, scale=1.0)
    animator.add_sprite("cat", cat)
    
    # 4. Define AI behavior
    class CatAI:
        def __init__(self, sprite: AnimatedSprite):
            self.sprite = sprite
            self.target_x = sprite.x
            self.state = "idle" # idle or walk
            self.state_time = 0.0
            self.speed = 150 # pixels per second
            
        def update(self, dt: float):
            self.state_time -= dt
            
            if self.state_time <= 0:
                # Decide next state
                if self.state == "idle":
                    self.state = "walk"
                    self.target_x = random.randint(100, SCREEN_WIDTH - 200)
                    self.state_time = abs(self.target_x - self.sprite.x) / self.speed
                else:
                    self.state = "idle"
                    self.state_time = random.uniform(2, 5)
            
            # Move towards target
            if self.state == "walk":
                dx = self.target_x - self.sprite.x
                if abs(dx) > 5:
                    step = (self.speed * dt) * (1 if dx > 0 else -1)
                    self.sprite.x += step
                    self.sprite.playing = True
                else:
                    self.sprite.x = self.target_x
                    self.sprite.playing = False
            else:
                self.sprite.playing = False # Stop animation while idle
                
    ai = CatAI(cat)
    
    # Hook the AI update into the loop (simple manual way for this demo)
    original_update = cat.update
    def custom_update(dt: float):
        ai.update(dt)
        original_update(dt)
        
    cat.update = custom_update
    
    print("Cat avatar running! Press Ctrl+C in terminal to stop.")
    print("The cat will wander randomly across the bottom of your screen.")
    
    animator.run()

if __name__ == "__main__":
    main()
