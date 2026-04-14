import ctypes
import os
from ctypes import Structure, c_int, POINTER, c_ubyte, c_bool
from pathlib import Path

# Resolve DLL path relative to the project structure
DEFAULT_DLL = Path(__file__).resolve().parent.parent.parent / "bin" / "engine.dll"

class Rect(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("w", c_int),
        ("h", c_int),
        ("r", c_ubyte),
        ("g", c_ubyte),
        ("b", c_ubyte),
        ("a", c_ubyte),
    ("layer_id", c_int),
]

class MouseEvent(Structure):
    _fields_ = [
        ("type", c_int),
        ("x", c_int),
        ("y", c_int),
        ("button", c_int),
    ]

# Event types (must match types.h)
MOUSE_DOWN = 1
MOUSE_UP = 2
MOUSE_MOVE = 3

class WindowEngine:
    def __init__(self, dll_path=None, pool_size=500):
        """
        Load the engine DLL and initialize the window pool.
        """
        if dll_path is None:
            dll_path = DEFAULT_DLL
        else:
            dll_path = Path(dll_path).resolve()
            
        if not dll_path.exists():
            raise FileNotFoundError(f"Engine DLL not found at: {dll_path}")
            
        # On Python 3.8+, we need to add the DLL directory to the search path
        # to ensure dependencies (like pthreads) are found.
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(str(dll_path.parent))
            
        # winmode=0 is sometimes required on Windows to use the standard search path
        try:
            self.lib = ctypes.CDLL(str(dll_path), winmode=0)
        except (TypeError, OSError):
            self.lib = ctypes.CDLL(str(dll_path))

        # Method signatures
        self.lib.InitEngine.argtypes = [c_int]
        self.lib.RenderFrame.argtypes = [POINTER(Rect), c_int]
        self.lib.RenderLayer.argtypes = [c_int, POINTER(Rect), c_int]
        self.lib.SetLayerConfig.argtypes = [c_int, c_int, c_bool]
        self.lib.SetTransparencyMode.argtypes = [c_bool, c_ubyte, c_ubyte, c_ubyte]
        self.lib.GrowPool.argtypes = [c_int]
        self.lib.PollEvents.argtypes = [POINTER(MouseEvent), c_int]
        self.lib.PollEvents.restype = c_int
        self.lib.CloseEngine.argtypes = []

        # Initialize the engine
        self.lib.InitEngine(pool_size)

    def render(self, rect_list):
        """
        Render a flat list of rectangles (using the default layer).
        rect_list can be a list of tuples or a NumPy array with the correct dtype.
        """
        self._render_generic(self.lib.RenderFrame, rect_list)

    def poll_events(self, max_count=64):
        """
        Poll for input events from the engine.
        Returns a list of MouseEvent objects.
        """
        event_array = (MouseEvent * max_count)()
        count = self.lib.PollEvents(event_array, max_count)
        return [event_array[i] for i in range(count)]

    def render_layer(self, layer_id, rect_list):
        """
        Render a list of rectangles to a specific layer.
        """
        def call_render(ptr, count):
            self.lib.RenderLayer(layer_id, ptr, count)
        
        self._render_generic(call_render, rect_list)

    def set_transparency(self, enable, r=255, g=0, b=255):
        """
        Enable/disable transparency (color-keying). Default is magenta (255, 0, 255).
        """
        self.lib.SetTransparencyMode(enable, r, g, b)

    def set_layer_config(self, layer_id, z_order, visible=True):
        """
        Configure a specific layer's properties.
        """
        self.lib.SetLayerConfig(layer_id, z_order, visible)

    def grow_pool(self, additional_count):
        """
        Add more windows to the pool at runtime.
        """
        self.lib.GrowPool(additional_count)

    def _render_generic(self, render_func, rect_list):
        import numpy as np

        if isinstance(rect_list, np.ndarray):
            count = len(rect_list)
            # If it's a structured array with compatible fields, pass it directly
            # Ensure the dtype matches Rect structure
            try:
                render_func(rect_list.ctypes.data_as(POINTER(Rect)), count)
            except Exception:
                # Fallback if dtype is incompatible
                self._render_fallback(render_func, rect_list)
        else:
            self._render_fallback(render_func, rect_list)

    def _render_fallback(self, render_func, rect_list):
        count = len(rect_list)
        rect_array = (Rect * count)()
        for i, r in enumerate(rect_list):
            rect_array[i].x = int(r[0])
            rect_array[i].y = int(r[1])
            rect_array[i].w = int(r[2])
            rect_array[i].h = int(r[3])
            # Color support (defaults to white if not provided)
            rect_array[i].r = r[4] if len(r) > 4 else 255
            rect_array[i].g = r[5] if len(r) > 5 else 255
            rect_array[i].b = r[6] if len(r) > 6 else 255
            rect_array[i].a = r[7] if len(r) > 7 else 255
            rect_array[i].layer_id = r[8] if len(r) > 8 else 0
        
        render_func(rect_array, count)

    def close(self): 
        """
        Shutdown the engine and destroy all windows.
        """
        self.lib.CloseEngine()
