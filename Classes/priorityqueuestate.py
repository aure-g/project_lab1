from .state import State

class PriorityQueueState:
    def __init__(self):
        """Initialize an empty priority queue storing (State, cost) tuples."""
        # Stored in the queue as tuples (cube_state, state_cost)
        self.queue = []

    def is_empty(self):
        """Return True if the queue contains no states."""
        return len(self.queue)== 0

    def push(self, new_state:State):
        """Insert new_state or update it if a cheaper path to the same cube config exists."""
        cost_to_goal = new_state.valH if new_state.valH is not None else 0
        new_state_cost = new_state.nbrActions + cost_to_goal

        for i, (explored_state, explored_cost) in enumerate(self.queue):
            # Checking if we already know this cube state
            if (explored_state.cube == new_state.cube):
                if (new_state_cost < explored_cost):
                    self.queue[i] = (new_state, new_state_cost) # we replace the already existing cube state with an improved cost and a state reached with a different path
                    self.sort()
                return
        # Case the configuration is new 
        self.queue.append((new_state, new_state_cost))
        self.sort()
    
    def sort(self):
        """Sort the queue in ascending order of total cost f = g + h."""
        # we sort using only the cost, we do not sort the tuples as a whole
        self.queue.sort(key= lambda x : x[1])

    def pop(self) -> State|None :
        """Remove and return the state with the lowest f-cost, or None if empty."""
        if (not self.is_empty()):
            best_state, best_cost = self.queue.pop(0)
            return best_state
        return None

