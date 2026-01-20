import ctypes
from ctypes import Structure, c_int, POINTER, c_ubyte

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
    ]

class WindowEngine:
    def __init__(self, dll_path=r"D:\\windonimation\\bin\\engine.dll", pool_size=500):
        """
        load dll
        """
        self.lib = ctypes.CDLL(dll_path)

        # method signatures
        self.lib.InitEngine.argtypes = [c_int]
        self.lib.RenderFrame.argtypes = [POINTER(Rect), c_int]

        # init
        self.lib.InitEngine(pool_size)

    def render(self, rect_list):
        """
        convert python list or numpy array of coordinates to c-array
        """
        import numpy as np

        if isinstance(rect_list, np.ndarray):
            count = len(rect_list)
            # If it's a structured array, we can pass it directly
            self.lib.RenderFrame(rect_list.ctypes.data_as(POINTER(Rect)), count)
        else:
            count = len(rect_list)
            # Legacy path update for color support (defaults to white if not provided)
            # rect_list entries can be (x, y, w, h) or (x, y, w, h, r, g, b)
            rect_array = (Rect * count)()
            for i, r in enumerate(rect_list):
                rect_array[i].x = r[0]
                rect_array[i].y = r[1]
                rect_array[i].w = r[2]
                rect_array[i].h = r[3]
                rect_array[i].r = r[4] if len(r) > 4 else 255
                rect_array[i].g = r[5] if len(r) > 5 else 255
                rect_array[i].b = r[6] if len(r) > 6 else 255
                rect_array[i].a = 255
            
            self.lib.RenderFrame(rect_array, count)

    def close(self): 
        """
        close the instance after animation completes
        """
        self.lib.CloseEngine()
