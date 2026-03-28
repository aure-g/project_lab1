from cube import Cube
from ..Enumerations.action_type import ActionType

class State:
    def __init__(self, cube: Cube, nbActions: int, parentState: State | None, actionType: ActionType):
        self.cube: Cube = cube
        self.nbrActions: int = nbActions
        self.pere: State | None = parentState
        self.actionPere: ActionType = actionType
        self.valH: None = None
        
    def expand(self) -> list[State]:
        children_states: list[State] = []
        
        new_cube: Cube = self.cube.copy()
        new_cube.turnUp()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.TURN_UP))
        
        new_cube = self.cube.copy()
        new_cube.turnLeft()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.TURN_LEFT))
        
        new_cube = self.cube.copy()
        new_cube.turnFront()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.TURN_FRONT))
        
        new_cube = self.cube.copy()
        new_cube.turnRight()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.TURN_RIGHT))
        
        new_cube = self.cube.copy()
        new_cube.turnDown()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.TURN_DOWN))
        
        new_cube = self.cube.copy()
        new_cube.turnBack()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.TURN_BACK))
        
        new_cube = self.cube.copy()
        new_cube.returnUp()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.RETURN_UP))
        
        new_cube = self.cube.copy()
        new_cube.returnLeft()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.RETURN_LEFT))
        
        new_cube = self.cube.copy()
        new_cube.returnFront()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.RETURN_FRONT))
        
        new_cube = self.cube.copy()
        new_cube.returnRight()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.RETURN_RIGHT))
        
        new_cube = self.cube.copy()
        new_cube.returnDown()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.RETURN_DOWN))
        
        new_cube = self.cube.copy()
        new_cube.returnBack()
        children_states.append(State(new_cube, self.nbrActions + 1, self, ActionType.RETURN_BACK))
        
        return children_states