import math
from .fire_chicken.mouse_position import MousePosition

def compute_mouse_position_with_direction_and_magnitude(direction: float, magnitude: int):
    direction_in_radians = direction*math.pi/180
    horizontal = magnitude*math.cos(direction_in_radians)
    vertical = -magnitude*math.sin(direction_in_radians)
    position = MousePosition(horizontal, vertical)
    return position

def change_mouse_position_by(change: MousePosition):
    new_position: MousePosition = MousePosition.current() + change
    new_position.go()