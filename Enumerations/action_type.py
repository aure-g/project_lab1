from enum import Enum

class ActionType(Enum):
    """All 12 possible quarter-turn moves on a Rubik's cube (6 clockwise + 6 counter-clockwise)."""
    TURN_UP = 0       # U  — top face clockwise
    TURN_LEFT = 1     # L  — left face clockwise
    TURN_FRONT = 2    # F  — front face clockwise
    TURN_RIGHT = 3    # R  — right face clockwise
    TURN_DOWN = 4     # D  — bottom face clockwise
    TURN_BACK = 5     # B  — back face clockwise
    RETURN_UP = 6     # U' — top face counter-clockwise
    RETURN_LEFT = 7   # L' — left face counter-clockwise
    RETURN_FRONT = 8  # F' — front face counter-clockwise
    RETURN_RIGHT = 9  # R' — right face counter-clockwise
    RETURN_DOWN = 10  # D' — bottom face counter-clockwise
    RETURN_BACK = 11  # B' — back face counter-clockwise