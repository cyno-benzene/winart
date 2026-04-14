from PIL import Image
import os

def generate_cat_sprite_sheet():
    """
    Generates a simple 16x16 pixel art cat sprite sheet with 2 frames: idle and walk.
    """
    sheet = Image.new("RGBA", (32, 16), (0, 0, 0, 0)) # 2 frames, each 16x16
    
    cat_color = (255, 165, 0, 255) # Orange cat
    eye_color = (0, 255, 0, 255) # Green eyes
    nose_color = (255, 105, 180, 255) # Pink nose
    
    def draw_cat(offset_x, frame_idx):
        # Body
        for y in range(8, 14):
            for x in range(4, 13):
                sheet.putpixel((offset_x + x, y), cat_color)
        
        # Head
        for y in range(4, 9):
            for x in range(6, 11):
                sheet.putpixel((offset_x + x, y), cat_color)
        
        # Ears
        sheet.putpixel((offset_x + 6, 3), cat_color)
        sheet.putpixel((offset_x + 10, 3), cat_color)
        
        # Eyes
        sheet.putpixel((offset_x + 7, 6), eye_color)
        sheet.putpixel((offset_x + 9, 6), eye_color)
        
        # Nose
        sheet.putpixel((offset_x + 8, 7), nose_color)
        
        # Tail (idle vs walk)
        tail_y = 10 if frame_idx == 0 else 9
        for x in range(1, 4):
            sheet.putpixel((offset_x + x, tail_y), cat_color)
            
        # Legs (idle vs walk)
        if frame_idx == 0:
            sheet.putpixel((offset_x + 5, 14), cat_color)
            sheet.putpixel((offset_x + 11, 14), cat_color)
        else:
            sheet.putpixel((offset_x + 6, 14), cat_color)
            sheet.putpixel((offset_x + 10, 14), cat_color)

    draw_cat(0, 0)  # Frame 1: Idle
    draw_cat(16, 1) # Frame 2: Walk

    if not os.path.exists("demo/assets"):
        os.makedirs("demo/assets")
    
    sheet.save("demo/assets/cat_sprite.png")
    print("Generated demo/assets/cat_sprite.png")

if __name__ == "__main__":
    generate_cat_sprite_sheet()
