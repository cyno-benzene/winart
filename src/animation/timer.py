import time

class FrameTimer:
    """
    A precise frame timer that uses time.perf_counter for sub-millisecond precision.
    Helps maintain a stable frame rate without sleep drift.
    """
    def __init__(self, target_fps: float = 60.0):
        self.target_fps = target_fps
        self.frame_duration = 1.0 / target_fps
        self.last_tick = time.perf_counter()

    def tick(self) -> float:
        """
        Wait for the next frame and return the time since the last tick (dt).
        """
        now = time.perf_counter()
        elapsed = now - self.last_tick
        
        # Calculate how much time is left until the next frame
        remaining = self.frame_duration - elapsed
        
        if remaining > 0:
            # On Windows, time.sleep() has ~15ms precision.
            # We sleep most of the way, then busy-wait for the last millisecond for accuracy.
            if remaining > 0.001:
                time.sleep(remaining - 0.001)
            
            # Busy wait
            while (time.perf_counter() - self.last_tick) < self.frame_duration:
                pass
            
            now = time.perf_counter()
            dt = now - self.last_tick
        else:
            # We're running behind!
            dt = elapsed
            
        self.last_tick = now
        return dt
