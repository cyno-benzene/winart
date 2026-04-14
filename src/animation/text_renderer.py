from PIL import Image, ImageDraw
from typing import List, Tuple
from .sprite import PixelFrame

class TextRenderer:
    """
    Renders dynamic text into a PixelFrame using Pillow.
    """
    @staticmethod
    def render_text(text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> PixelFrame:
        # Create a temporary image to measure text (rough estimate)
        # In a real app, we'd use font.getbbox or similar
        char_width = 8
        char_height = 12
        img_width = len(text) * char_width
        img_height = char_height
        
        if img_width == 0:
            return PixelFrame()
            
        img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw text with default font (usually very small/pixelated if not specified)
        draw.text((0, 0), text, fill=(color[0], color[1], color[2], 255))
        
        frame = PixelFrame()
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                if isinstance(pixel, (tuple, list)) and len(pixel) >= 4:
                    if int(pixel[3]) > 128: # Use a threshold for alpha
                        frame.pixels.append((x, y, color[0], color[1], color[2]))
                        
        return frame
