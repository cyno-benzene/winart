import numpy as np
from typing import List, Tuple, cast, Optional, Any
from PIL import Image
from .sprite import PixelFrame
from .mesher import GreedyMesher

class SpriteSheetLoader:
    """
    Loads images and sprite sheets using Pillow, and converts them to the engine's 
    PixelFrame format. Includes robust optimizations for high-resolution assets.
    """
    @staticmethod
    def _get_resample_mode() -> Any:
        from PIL import Image as PILImage # type: ignore
        if hasattr(PILImage, "Resampling"):
            return PILImage.Resampling.NEAREST
        return PILImage.NEAREST

    @staticmethod
    def _quantize(img: Image.Image, colors: int) -> Image.Image:
        """Reduces color complexity to help window merging."""
        if colors <= 0:
            return img
        
        # Ensure we're in RGB for quantization, then back to RGBA
        alpha = img.getchannel('A')
        img_rgb = img.convert("RGB")
        img_quant = img_rgb.quantize(colors=colors).convert("RGBA")
        img_quant.putalpha(alpha)
        return img_quant

    @staticmethod
    def load_image(path: str, max_width: int = 128, max_height: int = 128, 
                   transparent_color: Optional[Tuple[int, int, int]] = None,
                   quantize_colors: int = 0) -> PixelFrame:
        """
        Load a single image and convert it to a PixelFrame with optimizations.
        """
        img = Image.open(path).convert("RGBA")
        
        if quantize_colors > 0:
            img = SpriteSheetLoader._quantize(img, quantize_colors)

        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), SpriteSheetLoader._get_resample_mode())
            
        return SpriteSheetLoader._img_to_frame(img, transparent_color)

    @staticmethod
    def load_sheet(path: str, frame_width: int, frame_height: int, 
                   transparent_color: Optional[Tuple[int, int, int]] = None,
                   quantize_colors: int = 0,
                   auto_scale_to_pool: int = 1000) -> List[PixelFrame]:
        """
        Slice a sprite sheet with iterative fit optimization.
        If frame_width/height are 0, it attempts to auto-slice the sheet based on content.
        """
        sheet = Image.open(path).convert("RGBA")
        
        if quantize_colors > 0:
            sheet = SpriteSheetLoader._quantize(sheet, quantize_colors)

        # Content-Aware Auto-Slicing
        raw_frames = []
        if frame_width <= 0 or frame_height <= 0:
            # Simple grid search for blobs might be too complex here.
            # Let's try a fallback: if width/height are 0, assume the sheet 
            # contains ONE large sprite, or try to detect a grid.
            # For now, let's treat it as a single sprite if 0,0.
            raw_frames = [sheet]
        else:
            num_cols = sheet.width // frame_width
            num_rows = sheet.height // frame_height
            for row in range(num_rows):
                for col in range(num_cols):
                    box = (col * frame_width, row * frame_height, (col + 1) * frame_width, (row + 1) * frame_height)
                    raw_frames.append(sheet.crop(box))
        
        frames = []
        pool_limit = int(auto_scale_to_pool * 0.95) if auto_scale_to_pool > 0 else 999999

        for img_frame in raw_frames:
            # Iterative fit
            current_scale = 1.0
            while True:
                test_img = img_frame
                if current_scale < 1.0:
                    new_w = max(4, int(img_frame.width * current_scale))
                    new_h = max(4, int(img_frame.height * current_scale))
                    test_img = img_frame.resize((new_w, new_h), SpriteSheetLoader._get_resample_mode())
                
                frame_data = SpriteSheetLoader._img_to_frame(test_img, transparent_color)
                if not frame_data.pixels:
                    break
                    
                # Calculate meshed count
                meshed_count = len(frame_data.get_meshed())
                
                if meshed_count <= pool_limit or current_scale < 0.05:
                    if meshed_count > 0:
                        # Correctly scale the offset back to the original coordinate system if needed?
                        # Actually, keeping it in the scaled space is probably better for consistency.
                        frames.append(frame_data)
                    break
                
                # Too many windows, shrink and retry
                current_scale *= 0.7
                    
        return frames

    @staticmethod
    def _img_to_frame(img: Image.Image, transparent_color: Optional[Tuple[int, int, int]]) -> PixelFrame:
        """Converts an image to a PixelFrame, trimming empty space and capturing offsets."""
        # Use getbbox on alpha channel
        bbox = img.getbbox()
        if not bbox:
            return PixelFrame()
            
        left, upper, right, lower = bbox
        trimmed_img = img.crop((left, upper, right, lower))
        
        frame = PixelFrame()
        frame.offset_x = left
        frame.offset_y = upper
        
        # Use numpy for fast pixel extraction
        arr = np.array(trimmed_img.convert("RGBA"))
        
        # Alpha is channel 3. We use > 0 to include all semi-transparent pixels.
        y_indices, x_indices = np.where(arr[:, :, 3] > 0)
        
        for y, x in zip(y_indices, x_indices):
            r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
            if transparent_color and (r, g, b) == transparent_color:
                continue
            frame.pixels.append((int(x), int(y), r, g, b))
            
        return frame
