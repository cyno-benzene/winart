import os
import random
import time
import argparse
from src.animation import (
    Animator, SpriteSheetLoader, AnimatedSprite, DraggableSprite,
    AnimationStateMachine, TextRenderer, PixelSprite
)

# Configuration
PIXEL_SIZE = 8
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

def main():
    parser = argparse.ArgumentParser(description="Clippy 2.0 Desktop Assistant")
    parser.add_argument("--sheet", type=str, help="Path to custom sprite sheet")
    parser.add_argument("--width", type=int, default=32, help="Frame width in sprite sheet")
    parser.add_argument("--height", type=int, default=32, help="Frame height in sprite sheet")
    parser.add_argument("--chroma", type=str, help="Transparent color in hex (e.g. FF00FF)")
    parser.add_argument("--colors", type=int, default=16, help="Quantize colors to help performance")
    parser.add_argument("--pool", type=int, default=1024, help="Window pool size")
    parser.add_argument("--scale", type=float, default=2.0, help="Scale multiplier for sprite")
    parser.add_argument("--pixel-size", type=int, default=8, help="Physical size of one window pixel")
    parser.add_argument("--debug", action="store_true", help="Enable debug bounding box")
    args = parser.parse_args()

    print("Initializing Clippy 2.0...")
    
    # 1. Setup Animator
    animator = Animator(pool_size=args.pool, pixel_size=args.pixel_size)
    animator.engine.set_transparency(True)
    
    # 2. Load Assets
    transparent_color = None
    if args.chroma:
        c = args.chroma.lstrip('#')
        if len(c) == 6:
            r = int(c[0:2], 16)
            g = int(c[2:4], 16)
            b = int(c[4:6], 16)
            transparent_color = (r, g, b)

    assets_path = args.sheet if args.sheet else os.path.join("demo", "assets", "clippy_sprites.png")
    if not os.path.exists(assets_path):
        if not args.sheet:
            print("Clippy assets not found. Run demo/generate_clippy.py first.")
        else:
            print(f"Custom sprite sheet not found at: {assets_path}")
        return
        
    print(f"Loading sheet: {assets_path} (Quantizing to {args.colors} colors)")
    all_frames = SpriteSheetLoader.load_sheet(
        assets_path, 
        args.width, 
        args.height, 
        transparent_color=transparent_color,
        quantize_colors=args.colors,
        auto_scale_to_pool=args.pool
    )
    
    if len(all_frames) < 1:
        print("No frames loaded from sprite sheet!")
        return

    # Map frames to animations
    idle_frame = [all_frames[0]]
    blink_frames = [all_frames[0], all_frames[1 % len(all_frames)], all_frames[0]]
    wave_frames = [all_frames[2 % len(all_frames)], all_frames[3 % len(all_frames)]]
    
    # 3. Create Clippy
    clippy = DraggableSprite(idle_frame, fps=4, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2, scale=args.scale)
    clippy.debug_box = args.debug
    clippy.ensure_visible(SCREEN_WIDTH, SCREEN_HEIGHT, pixel_size=args.pixel_size)
    animator.add_sprite("clippy", clippy)
    
    # 4. Setup State Machine
    sm = AnimationStateMachine(clippy)
    sm.add_state("idle", idle_frame, loop=True)
    sm.add_state("blink", blink_frames, fps=8, loop=False)
    sm.add_state("wave", wave_frames, fps=6, loop=True)
    sm.set_state("idle")
    
    # 5. Speech Bubble Sprite
    # Initially hidden
    bubble_frame = TextRenderer.render_text("It looks like you're writing code!")
    bubble = PixelSprite(bubble_frame, x=clippy.x + 50, y=clippy.y - 50, scale=args.scale * 0.75)
    bubble.visible = False
    animator.add_sprite("bubble", bubble)
    
    # 6. AI Logic
    class ClippyAI:
        def __init__(self, clippy, bubble, sm):
            self.clippy = clippy
            self.bubble = bubble
            self.sm = sm
            self.timer = 0.0
            self.bubble_timer = 0.0
            self.last_x, self.last_y = clippy.x, clippy.y
            self.speed_accum = 0.0
            
        def update(self, dt):
            self.timer += dt
            self.sm.update(dt)
            
            # Position bubble relative to clippy
            self.bubble.x = self.clippy.x + 32 * self.clippy.scale * 0.8
            self.bubble.y = self.clippy.y - 10 * self.clippy.scale
            
            # Ensure visible every frame
            self.clippy.ensure_visible(SCREEN_WIDTH, SCREEN_HEIGHT, pixel_size=args.pixel_size)
            
            # Check for rapid movement (Dizzy trigger)
            dx = self.clippy.x - self.last_x
            dy = self.clippy.y - self.last_y
            speed = (dx**2 + dy**2)**0.5 / dt
            self.speed_accum = self.speed_accum * 0.9 + speed * 0.1
            
            if self.speed_accum > 1500 and not self.bubble.visible:
                self.show_message("Woah! I'm dizzy!")
                self.speed_accum = 0

            self.last_x, self.last_y = self.clippy.x, self.clippy.y

            # Random behaviors when idle
            if self.sm.current_state and self.sm.current_state.name == "idle" and self.timer > 3.0:
                self.timer = 0
                r = random.random()
                if r < 0.2:
                    self.sm.set_state("blink")
                elif r < 0.4:
                    self.sm.set_state("wave")
                    self.timer = -2.0 # Wait 2 seconds of wave before returning to idle
                elif r < 0.5:
                    messages = [
                        "I'm here to help!",
                        "Nice code!",
                        "Need a plan?",
                        "Don't forget to save!",
                        "Real windows, real pixels!"
                    ]
                    self.show_message(random.choice(messages))
            
            # Transition back to idle if wave timer finished
            if self.sm.current_state and self.sm.current_state.name == "wave" and self.timer >= 0:
                self.sm.set_state("idle")
                
            # If blinking completed (sm.update stops playback), return to idle
            if self.sm.current_state and self.sm.current_state.name == "blink" and not self.clippy.playing:
                self.sm.set_state("idle")

            # Manage bubble visibility
            if self.bubble.visible:
                self.bubble_timer -= dt
                if self.bubble_timer <= 0:
                    self.bubble.visible = False

        def show_message(self, text):
            self.bubble.frame = TextRenderer.render_text(text)
            self.bubble.visible = True
            self.bubble_timer = 4.0
            
    ai = ClippyAI(clippy, bubble, sm)
    
    # Simple hook for AI update
    original_clippy_update = clippy.update
    def ai_clippy_update(dt):
        ai.update(dt)
        original_clippy_update(dt)
    
    clippy.update = ai_clippy_update
    
    # 7. Start the show
    print("Clippy is active! Features:")
    print(" - Drag him with the left mouse button")
    print(" - Random idle animations (blink, wave)")
    print(" - Occasional advice via speech bubbles")
    print(" - '2D Greedy Meshing' optimization active")
    if args.sheet:
        print(f" - Using custom sprite sheet: {args.sheet}")
    print(f" - Pixel size: {args.pixel_size}, Scale: {args.scale}")
    print("\nPress Ctrl+C to stop.")
    
    animator.run()

if __name__ == "__main__":
    main()
