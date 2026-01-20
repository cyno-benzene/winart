import time
import numpy as np
from src.wrapper.winart import WindowEngine

# CONFIGURATION
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 15
BALL_SPEED_X = 10
BALL_SPEED_Y = 10
AI_SPEED = 8

# Initialize Engine
engine = WindowEngine(pool_size=3) # 2 paddles + 1 ball

# Game State
p1_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
p2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

def get_game_rects():
    # Efficiently create NumPy array for 3 windows with color support
    rect_data = np.zeros(3, dtype=[('x', 'i4'), ('y', 'i4'), ('w', 'i4'), ('h', 'i4'),
                                   ('r', 'u1'), ('g', 'u1'), ('b', 'u1'), ('a', 'u1')])
    
    # Paddle 1 (Left) - Green
    rect_data[0] = (50, int(p1_y), PADDLE_WIDTH, PADDLE_HEIGHT, 0, 255, 0, 255)
    
    # Paddle 2 (Right) - Red
    rect_data[1] = (SCREEN_WIDTH - 50 - PADDLE_WIDTH, int(p2_y), PADDLE_WIDTH, PADDLE_HEIGHT, 255, 0, 0, 255)
    
    # Ball - Yellow
    rect_data[2] = (int(ball_x), int(ball_y), BALL_SIZE, BALL_SIZE, 255, 255, 0, 255)
    
    return rect_data

print("Ping Pong starting... Controls: W/S for Left. AI controls Right. ESC to quit.")

try:
    while True:
        # 1. Handle Input
        import ctypes
        GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState
        
        if GetAsyncKeyState(0x1B): # ESC
            break
        
        # Player 1 (Left)
        if GetAsyncKeyState(0x57): # W
            p1_y = max(0, p1_y - PADDLE_SPEED)
        if GetAsyncKeyState(0x53): # S
            p1_y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, p1_y + PADDLE_SPEED)
            
        # AI Control for Paddle 2 (Right)
        p2_center = p2_y + PADDLE_HEIGHT // 2
        if p2_center < ball_y:
            p2_y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, p2_y + AI_SPEED)
        elif p2_center > ball_y:
            p2_y = max(0, p2_y - AI_SPEED)

        # 2. Update Ball Position
        ball_x += ball_dx
        ball_y += ball_dy

        # 3. Collision with Top/Bottom
        if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
            ball_dy *= -1

        # 4. Collision with Paddles
        # Paddle 1
        if ball_x <= 50 + PADDLE_WIDTH and p1_y < ball_y + BALL_SIZE and p1_y + PADDLE_HEIGHT > ball_y:
            ball_dx = abs(ball_dx)
        
        # Paddle 2
        if ball_x >= SCREEN_WIDTH - 50 - PADDLE_WIDTH - BALL_SIZE and p2_y < ball_y + BALL_SIZE and p2_y + PADDLE_HEIGHT > ball_y:
            ball_dx = -abs(ball_dx)

        # 5. Score / Reset
        if ball_x < 0 or ball_x > SCREEN_WIDTH:
            ball_x = SCREEN_WIDTH // 2
            ball_y = SCREEN_HEIGHT // 2
            ball_dx *= -1

        # 6. Render
        rects = get_game_rects()
        engine.render(rects)
        
        time.sleep(0.016) # ~60 FPS

except KeyboardInterrupt:
    pass
finally:
    engine.close()
