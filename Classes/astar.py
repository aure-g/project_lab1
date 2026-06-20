from .state import State
from .priorityqueuestate import PriorityQueueState
from Enumerations.action_type import ActionType

class Astar:
    def __init__(self, initial_state):
        self.state: State = initial_state # The cube once scrambled, before the first moves to solve it
        # We store explored cubes as strings to compare configurations,
        # not Python object identities.
        self.explored: set[str] = set()
        self.frontier = PriorityQueueState()

    def add(self, state):
        self.explored.add(str(state.cube))

    def contains(self, state):
        return str(state.cube) in self.explored
    
    # Returns the set of actions needed to reach the solution
    def solve(self) -> list[ActionType]:
        self.frontier.push(self.state)

        while (not self.frontier.is_empty()):
            current_state = self.frontier.pop()

            if current_state.cube.isSolved():
                print("The solution has been found. These are the winning moves in order : ")
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