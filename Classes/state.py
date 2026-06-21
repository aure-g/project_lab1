from typing import Optional
from collections.abc import Callable

from .cube import Cube
import copy
from Enumerations.action_type import ActionType

# Maps each ActionType to the corresponding Cube method so callers can apply a move without a switch.
ACTIONS: dict[ActionType, Callable[[Cube], None]] = {
    ActionType.TURN_UP:      Cube.turnUp,
    ActionType.TURN_LEFT:    Cube.turnLeft,
    ActionType.TURN_FRONT:   Cube.turnFront,
    ActionType.TURN_RIGHT:   Cube.turnRight,
    ActionType.TURN_DOWN:    Cube.turnDown,
    ActionType.TURN_BACK:    Cube.turnBack,
    ActionType.RETURN_UP:    Cube.returnUp,
    ActionType.RETURN_LEFT:  Cube.returnLeft,
    ActionType.RETURN_FRONT: Cube.returnFront,
    ActionType.RETURN_RIGHT: Cube.returnRight,
    ActionType.RETURN_DOWN:  Cube.returnDown,
    ActionType.RETURN_BACK:  Cube.returnBack,
}

class State:
    def __init__(self, cube: Cube, nbActions: int, parentState: Optional['State'], actionType: Optional[ActionType]):
        """Initialize a search state with its cube config, path cost, parent, and heuristic value."""
        self.cube: Cube = cube
        self.nbrActions: int = nbActions
        self.father: State | None = parentState
        self.fatherAction: Optional[ActionType] = actionType # The action which led to the current state from the pere(father) state
        from .heuristiclabel import HeuristicLabel
        self.valH: int = HeuristicLabel.value(self) # Estimated number of moves left to solve the cube

    def expand(self) -> list['State']:
        """Return all successor states obtained by applying each possible action."""
        children_states = []
        for action_type, method in ACTIONS.items():
            new_cube = copy.deepcopy(self.cube)
            method(new_cube)
            children_states.append(State(new_cube, self.nbrActions + 1, self, action_type))
        return children_states
