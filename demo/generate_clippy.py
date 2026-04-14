import os
from PIL import Image, ImageDraw

def create_clippy_frame(draw, x_offset, frame_type):
    # Colors
    CLIP_COLOR = (240, 240, 100) # Yellowish
    EYE_COLOR = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    # Body (a more curvy paperclip)
    # Using multiple segments to form the spiral
    center_x = 16 + x_offset
    center_y = 16
    
    # Simple spiral-like shape with lines
    points = [
        (10, 15), (10, 25), (22, 25), (22, 8), (8, 8), (8, 20), (18, 20), (18, 12)
    ]
    
    # Draw thicker lines with "caps"
    for i in range(len(points) - 1):
        p1 = (points[i][0] + x_offset, points[i][1])
        p2 = (points[i+1][0] + x_offset, points[i+1][1])
        draw.line([p1, p2], fill=CLIP_COLOR, width=3)

    # Eyes (bigger, with whites)
    eye_x1, eye_x2 = 12 + x_offset, 20 + x_offset
    eye_y = 12
    
    if frame_type == "blink":
        draw.line([(eye_x1 - 2, eye_y), (eye_x1 + 2, eye_y)], fill=EYE_COLOR, width=1)
        draw.line([(eye_x2 - 2, eye_y), (eye_x2 + 2, eye_y)], fill=EYE_COLOR, width=1)
    else:
        # Left eye
        draw.ellipse([(eye_x1 - 3, eye_y - 4), (eye_x1 + 3, eye_y + 4)], fill=WHITE, outline=EYE_COLOR)
        draw.point((eye_x1, eye_y), fill=EYE_COLOR)
        # Right eye
        draw.ellipse([(eye_x2 - 3, eye_y - 4), (eye_x2 + 3, eye_y + 4)], fill=WHITE, outline=EYE_COLOR)
        draw.point((eye_x2, eye_y), fill=EYE_COLOR)

    # Eyebrows (for expression)
    if frame_type == "wave1" or frame_type == "wave2":
        # Surprised/Happy eyebrows
        draw.arc([(eye_x1 - 4, eye_y - 8), (eye_x1 + 4, eye_y - 4)], start=180, end=0, fill=EYE_COLOR)
        draw.arc([(eye_x2 - 4, eye_y - 8), (eye_x2 + 4, eye_y - 4)], start=180, end=0, fill=EYE_COLOR)
    else:
        draw.line([(eye_x1 - 2, eye_y - 6), (eye_x1 + 2, eye_y - 7)], fill=EYE_COLOR, width=1)
        draw.line([(eye_x2 - 2, eye_y - 7), (eye_x2 + 2, eye_y - 6)], fill=EYE_COLOR, width=1)

    # Mouth (smile)
    draw.arc([(12 + x_offset, 18), (20 + x_offset, 24)], start=0, end=180, fill=EYE_COLOR)

    # Hand for wave
    if frame_type == "wave1":
        draw.line([(24 + x_offset, 20), (30 + x_offset, 10)], fill=CLIP_COLOR, width=2)
    elif frame_type == "wave2":
        draw.line([(24 + x_offset, 20), (30 + x_offset, 25)], fill=CLIP_COLOR, width=2)

def main():
    os.makedirs("demo/assets", exist_ok=True)
    sheet = Image.new("RGBA", (32 * 4, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    
    create_clippy_frame(draw, 0, "idle")
    create_clippy_frame(draw, 32, "blink")
    create_clippy_frame(draw, 64, "wave1")
    create_clippy_frame(draw, 96, "wave2")
    
    sheet.save("demo/assets/clippy_sprites.png")
    print("Generated demo/assets/clippy_sprites.png")

if __name__ == "__main__":
    main()
