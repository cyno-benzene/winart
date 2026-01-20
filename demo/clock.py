from src.wrapper.winart import WindowEngine
import time
from datetime import datetime


engine = WindowEngine(pool_size = 100)

DIGITS = {
    '0': ["111", "101", "101", "101", "111"],
    '1': ["010", "110", "010", "010", "111"],
    '2': ["111", "001", "111", "100", "111"],
    '3': ["111", "001", "111", "001", "111"],
    '4': ["101", "101", "111", "001", "001"],
    '5': ["111", "100", "111", "001", "111"],
    '6': ["111", "100", "111", "101", "111"],
    '7': ["111", "001", "001", "001", "001"],
    '8': ["111", "101", "111", "101", "111"],
    '9': ["111", "101", "111", "001", "111"],
    ':': ["000", "010", "000", "010", "000"]
}

BLOCK_SIZE = 20  # Size of each "pixel" window
SPACING = 10     # Space between blocks
DIGIT_GAP = 80   # Space between digits

engine = WindowEngine(pool_size=300)

def get_clock_rects():
    now = datetime.now().strftime("%H:%M:%S")
    all_rects = []
    
    start_x, start_y = 400, 300 # Centerish on screen
    
    current_x = start_x
    for char in now:
        bitmap = DIGITS[char]
        for row_idx, row_str in enumerate(bitmap):
            for col_idx, bit in enumerate(row_str):
                if bit == "1":
                    # Calculate position for this specific block
                    x = current_x + (col_idx * (BLOCK_SIZE + 2))
                    y = start_y + (row_idx * (BLOCK_SIZE + 2))
                    all_rects.append((x, y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Move x to the right for the next digit
        current_x += DIGIT_GAP
        
    return all_rects

try:
    print("Clock running... Press Ctrl+C in terminal or ESC on desktop to quit.")
    while True:
        rects = get_clock_rects()
        engine.render(rects)
        time.sleep(0.1) # Update 10 times per second
except KeyboardInterrupt:
    pass
finally:
    engine.close()