import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple
from .mesher import GreedyMesher

@dataclass
class PixelFrame:
    """
    A single frame of a sprite, consisting of a list of pixel offsets and colors.
    Pixels are relative to the sprite's top-left corner (0,0).
    """
    # List of (dx, dy, r, g, b)
    pixels: List[Tuple[int, int, int, int, int]] = field(default_factory=list)
    # Relative offset for this frame (to maintain alignment across animations)
    offset_x: int = 0
    offset_y: int = 0
    # Precomputed meshed rects: (dx, dy, w, h, r, g, b)
    _meshed: List[Tuple[int, int, int, int, int, int, int]] = field(default_factory=list, init=False)

    def get_meshed(self):
        if not self._meshed:
            self._meshed = GreedyMesher.mesh_pixels(self.pixels)
        return self._meshed

class Sprite:
    """
    Base class for objects rendered by the engine.
    """
    def __init__(self, x=0, y=0, scale=1.0, layer_id=0):
        self.x = float(x)
        self.y = float(y)
        self.scale = float(scale)
        self.layer_id = layer_id
        self.visible = True
        self.debug_box = False

    def update(self, dt: float):
        """Override to implement sprite behavior."""
        pass

    def handle_event(self, event, pixel_size: int = 8) -> bool:
        """Override to handle input events (click, drag, etc.)"""
        return False

    def get_bounds(self, pixel_size: int = 8) -> Tuple[int, int, int, int]:
        """Returns the bounding box (min_x, min_y, max_x, max_y) in screen space."""
        # By default, just a pixel sized box. Subclasses should override.
        return (int(self.x), int(self.y), int(self.x + pixel_size), int(self.y + pixel_size))

    def ensure_visible(self, screen_w: int, screen_h: int, pixel_size: int = 8):
        """Adjusts x, y to keep the sprite within screen bounds."""
        bx1, by1, bx2, by2 = self.get_bounds(pixel_size)
        
        if bx1 < 0: self.x -= bx1
        if bx2 > screen_w: self.x -= (bx2 - screen_w)
        
        if by1 < 0: self.y -= by1
        # Leave some space for taskbar at the bottom
        if by2 > screen_h - 40: self.y -= (by2 - (screen_h - 40))

    def to_rects(self, pixel_size: int = 8) -> np.ndarray:
        """Override to convert the current state to Rect data."""
        return np.zeros(0)

    def _get_debug_rects(self, bx1, by1, bx2, by2) -> List[Tuple]:
        if not self.debug_box: return []
        # Return 4 lines for the box
        w = bx2 - bx1
        h = by2 - by1
        return [
            (bx1, by1, w, 1, 255, 0, 0, 255, self.layer_id), # top
            (bx1, by2, w, 1, 255, 0, 0, 255, self.layer_id), # bottom
            (bx1, by1, 1, h, 255, 0, 0, 255, self.layer_id), # left
            (bx2, by1, 1, h, 255, 0, 0, 255, self.layer_id)  # right
        ]

class PixelSprite(Sprite):
    """
    A sprite made of individual 'pixel' windows.
    """
    def __init__(self, frame: PixelFrame, x=0, y=0, scale=1.0, layer_id=0):
        super().__init__(x, y, scale, layer_id)
        self.frame = frame

    def get_bounds(self, pixel_size: int = 8) -> Tuple[int, int, int, int]:
        if not self.frame.pixels:
            return (int(self.x), int(self.y), int(self.x), int(self.y))
        
        p_size = int(pixel_size * self.scale)
        meshed = self.frame.get_meshed()
        
        # Calculate min/max including frame offsets
        min_dx = min(r[0] for r in meshed) + self.frame.offset_x
        min_dy = min(r[1] for r in meshed) + self.frame.offset_y
        max_dx = max(r[0] + r[2] for r in meshed) + self.frame.offset_x
        max_dy = max(r[1] + r[3] for r in meshed) + self.frame.offset_y
        
        return (
            int(self.x + min_dx * p_size),
            int(self.y + min_dy * p_size),
            int(self.x + max_dx * p_size),
            int(self.y + max_dy * p_size)
        )

    def to_rects(self, pixel_size: int = 8) -> np.ndarray:
        if not self.visible:
            return np.zeros(0)

        meshed = self.frame.get_meshed()
        p_size = int(pixel_size * self.scale)
        
        all_rects = []
        for i, (dx, dy, w, h, r, g, b) in enumerate(meshed):
            all_rects.append((
                int(self.x + (dx + self.frame.offset_x) * p_size), 
                int(self.y + (dy + self.frame.offset_y) * p_size), 
                int(w * p_size), int(h * p_size),
                r, g, b, 255,
                self.layer_id
            ))
            
        if self.debug_box:
            bx1, by1, bx2, by2 = self.get_bounds(pixel_size)
            all_rects.extend(self._get_debug_rects(bx1, by1, bx2, by2))

        if not all_rects: return np.zeros(0)
        
        rect_data = np.zeros(len(all_rects), dtype=[
            ('x', 'i4'), ('y', 'i4'), ('w', 'i4'), ('h', 'i4'),
            ('r', 'u1'), ('g', 'u1'), ('b', 'u1'), ('a', 'u1'),
            ('layer_id', 'i4')
        ])
        for i, val in enumerate(all_rects):
            rect_data[i] = val
        return rect_data

class AnimatedSprite(PixelSprite):
    """
    A sprite that cycles through multiple PixelFrames.
    """
    def __init__(self, frames: List[PixelFrame], fps: float = 8.0, x=0, y=0, scale=1.0, layer_id=0):
        super().__init__(frames[0] if frames else PixelFrame(), x, y, scale, layer_id)
        self.frames = frames
        self.fps = fps
        self.current_frame_idx = 0
        self.time_accum = 0.0
        self.playing = True

    def update(self, dt: float):
        if not self.playing or not self.frames:
            return

        self.time_accum += dt
        frame_duration = 1.0 / self.fps
        
        while self.time_accum >= frame_duration:
            self.time_accum -= frame_duration
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
            self.frame = self.frames[self.current_frame_idx]

class DraggableSprite(AnimatedSprite):
    """
    An animated sprite that can be clicked and dragged.
    """
    def __init__(self, frames: List[PixelFrame], fps: float = 8.0, x=0, y=0, scale=1.0, layer_id=0):
        super().__init__(frames, fps, x, y, scale, layer_id)
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def is_point_inside(self, x: int, y: int, pixel_size: int = 8) -> bool:
        bx1, by1, bx2, by2 = self.get_bounds(pixel_size)
        return bx1 <= x <= bx2 and by1 <= y <= by2

    def handle_event(self, event, pixel_size: int = 8) -> bool:
        from src.wrapper.winart import MOUSE_DOWN, MOUSE_UP, MOUSE_MOVE
        
        if event.type == MOUSE_DOWN:
            if self.is_point_inside(event.x, event.y, pixel_size):
                self.dragging = True
                self.drag_offset_x = event.x - self.x
                self.drag_offset_y = event.y - self.y
                return True # Event handled

        elif event.type == MOUSE_UP:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == MOUSE_MOVE:
            if self.dragging:
                self.x = event.x - self.drag_offset_x
                self.y = event.y - self.drag_offset_y
                return True
        return False

class SegmentedSprite(Sprite):
    """
    A sprite composed of multiple segments that follow each other.
    Useful for snake-like or tail-like movement.
    """
    def __init__(self, segment_frames: List[PixelFrame], segment_count: int, spacing: float = 20.0, x=0, y=0, scale=1.0, layer_id=0):
        super().__init__(x, y, scale, layer_id)
        self.spacing = spacing
        self.segment_frames = segment_frames
        self.positions = []
        for i in range(segment_count):
            self.positions.append([float(x), float(y)])

    def update(self, dt: float):
        # The head (positions[0]) follows the sprite's x, y
        self.positions[0][0] = self.x
        self.positions[0][1] = self.y

        # Each subsequent segment follows the one before it
        for i in range(1, len(self.positions)):
            prev_x, prev_y = self.positions[i-1]
            curr_x, curr_y = self.positions[i]
            
            dx = prev_x - curr_x
            dy = prev_y - curr_y
            dist = (dx**2 + dy**2)**0.5
            
            if dist > self.spacing:
                # Maintain the fixed spacing
                move_dist = dist - self.spacing
                self.positions[i][0] += (dx / dist) * move_dist
                self.positions[i][1] += (dy / dist) * move_dist

    def to_rects(self, pixel_size: int = 8) -> np.ndarray:
        if not self.visible or not self.segment_frames:
            return np.zeros(0)

        all_rect_data = []
        p_size = int(pixel_size * self.scale)

        for i, (sx, sy) in enumerate(self.positions):
            # Select frame for this segment
            frame = self.segment_frames[i % len(self.segment_frames)]
            meshed = frame.get_meshed()
            
            for dx, dy, w, h, r, g, b in meshed:
                all_rect_data.append((
                    int(sx + (dx + frame.offset_x) * p_size),
                    int(sy + (dy + frame.offset_y) * p_size),
                    int(w * p_size),
                    int(h * p_size),
                    r, g, b, 255,
                    self.layer_id
                ))
        
        if self.debug_box:
            # For segmented, debug box might be complex, just use head's bounds for now
            bx1, by1, bx2, by2 = self.get_bounds(pixel_size)
            all_rect_data.extend(self._get_debug_rects(bx1, by1, bx2, by2))

        if not all_rect_data:
            return np.zeros(0)

        rect_data = np.zeros(len(all_rect_data), dtype=[
            ('x', 'i4'), ('y', 'i4'), ('w', 'i4'), ('h', 'i4'),
            ('r', 'u1'), ('g', 'u1'), ('b', 'u1'), ('a', 'u1'),
            ('layer_id', 'i4')
        ])
        for i, val in enumerate(all_rect_data):
            rect_data[i] = val
        return rect_data

class DraggableSegmentedSprite(SegmentedSprite):
    """
    A segmented sprite that can be dragged by its head.
    """
    def __init__(self, segment_frames: List[PixelFrame], segment_count: int, spacing: float = 20.0, x=0, y=0, scale=1.0, layer_id=0):
        super().__init__(segment_frames, segment_count, spacing, x, y, scale, layer_id)
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def is_point_inside(self, x: int, y: int, pixel_size: int = 8) -> bool:
        # Check if point is inside the head segment
        p_size = int(pixel_size * self.scale)
        head_frame = self.segment_frames[0]
        meshed = head_frame.get_meshed()
        
        hx, hy = self.positions[0]
        for dx, dy, w, h, _, _, _ in meshed:
            if hx + (dx + head_frame.offset_x) * p_size <= x <= hx + (dx + head_frame.offset_x + w) * p_size and \
               hy + (dy + head_frame.offset_y) * p_size <= y <= hy + (dy + head_frame.offset_y + h) * p_size:
                return True
        return False

    def handle_event(self, event, pixel_size: int = 8) -> bool:
        from src.wrapper.winart import MOUSE_DOWN, MOUSE_UP, MOUSE_MOVE
        
        if event.type == MOUSE_DOWN:
            if self.is_point_inside(event.x, event.y, pixel_size):
                self.dragging = True
                self.drag_offset_x = event.x - self.x
                self.drag_offset_y = event.y - self.y
                return True

        elif event.type == MOUSE_UP:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == MOUSE_MOVE:
            if self.dragging:
                self.x = event.x - self.drag_offset_x
                self.y = event.y - self.drag_offset_y
                return True
        
        return False

