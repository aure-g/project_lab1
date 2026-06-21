from .state import State
from .priorityqueuestate import PriorityQueueState
from Enumerations.action_type import ActionType

class Astar:
    def __init__(self, initial_state):
        """Initialize A* with the scrambled cube as the starting state."""
        self.state: State = initial_state
        # We store explored cubes as strings to compare configurations,
        # not Python object identities.
        self.explored: set[str] = set()
        self.frontier = PriorityQueueState()

    def add(self, state):
        """Mark a state's cube configuration as explored."""
        self.explored.add(str(state.cube))

    def contains(self, state):
        """Return True if the state's cube configuration has already been explored."""
        return str(state.cube) in self.explored

    def solve(self) -> list[ActionType] | None:
        """Run A* and return the ordered list of moves to solve the cube, or None if unsolvable."""
        self.frontier.push(self.state)

        while (not self.frontier.is_empty()):
            current_state = self.frontier.pop()

            if current_state.cube.isSolved():
                moves = []
                current = current_state
                while current.pere is not None:
                    moves.append(current.actionPere)
                    current = current.pere 
                # we added the moves in the reverse order starting from the solution
                moves.reverse()
                return moves
            
            self.add(current_state)
            next_states = current_state.expand()

            for child in next_states :
                if not self.contains(child):
                    self.frontier.push(child)
        return None