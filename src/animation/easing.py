import math

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t

def ease_in_quad(t: float) -> float:
    return t * t

def ease_out_quad(t: float) -> float:
    return t * (2 - t)

def ease_in_out_quad(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t

def ease_out_bounce(t: float) -> float:
    """A bounce effect, useful for a falling cat landing."""
    if t < (1 / 2.75):
        return 7.5625 * t * t
    elif t < (2 / 2.75):
        t -= (1.5 / 2.75)
        return 7.5625 * t * t + 0.75
    elif t < (2.5 / 2.75):
        t -= (2.25 / 2.75)
        return 7.5625 * t * t + 0.9375
    else:
        t -= (2.625 / 2.75)
        return 7.5625 * t * t + 0.984375

def smooth_move(start_val: float, end_val: float, current_time: float, duration: float, easing_func=ease_in_out_quad) -> float:
    """Helper to calculate the current value of an animated property."""
    if current_time >= duration:
        return end_val
    t = max(0, min(1, current_time / duration))
    return lerp(start_val, end_val, easing_func(t))
