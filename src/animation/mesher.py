import numpy as np
from typing import List, Tuple

class GreedyMesher:
    @staticmethod
    def mesh_pixels(pixels: List[Tuple[int, int, int, int, int]]) -> List[Tuple[int, int, int, int, int, int, int]]:
        """
        Optimizes a pixel list using 2D Greedy Meshing.
        1. Merge adjacent pixels horizontally into strips.
        2. Merge identical adjacent strips vertically into larger rectangles.
        Returns a list of (dx, dy, width, height, r, g, b).
        """
        if not pixels:
            return []
        
        # Phase 1: Horizontal Merging
        sorted_pixels = sorted(pixels, key=lambda p: (p[1], p[0]))
        horizontal_strips = []
        current_strip = None # [dx, dy, w, 1, r, g, b]
        
        for p in sorted_pixels:
            dx, dy, r, g, b = p
            if current_strip is None:
                current_strip = [dx, dy, 1, 1, r, g, b]
            else:
                if (dy == current_strip[1] and 
                    dx == current_strip[0] + current_strip[2] and 
                    r == current_strip[4] and g == current_strip[5] and b == current_strip[6]):
                    current_strip[2] += 1
                else:
                    horizontal_strips.append(list(current_strip))
                    current_strip = [dx, dy, 1, 1, r, g, b]
        if current_strip:
            horizontal_strips.append(list(current_strip))

        # Phase 2: Vertical Merging
        # Sort strips by dx, w, then dy to find candidates for vertical merging
        # Strips can merge if they have same dx, same width, same color, and consecutive dy
        horizontal_strips.sort(key=lambda s: (s[0], s[2], s[4], s[5], s[6], s[1]))
        
        final_rects = []
        current_rect = None # [dx, dy, w, h, r, g, b]
        
        for s in horizontal_strips:
            dx, dy, w, h, r, g, b = s
            if current_rect is None:
                current_rect = list(s)
            else:
                if (dx == current_rect[0] and w == current_rect[2] and
                    r == current_rect[4] and g == current_rect[5] and b == current_rect[6] and
                    dy == current_rect[1] + current_rect[3]):
                    current_rect[3] += 1 # Extend height
                else:
                    final_rects.append(tuple(current_rect))
                    current_rect = list(s)
        if current_rect:
            final_rects.append(tuple(current_rect))
            
        return final_rects
