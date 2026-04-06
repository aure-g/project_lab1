from .state import State

class PriorityQueueState:
    def __init__(self):
        # Stored in the queue as tuples (cube_state, state_cost)
        self.queue = []

    def is_empty(self):
        return len(self.queue)== 0

    def push(self, new_state:State):
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
        # we sort using only the cost, we do not sort the tuples as a whole
        self.queue.sort(key= lambda x : x[1])

    # returns and remove the first element of the queue, that is the state with the lowest cost
    def pop(self) -> State :
        if (not self.is_empty()):
            best_state, best_cost = self.queue.pop(0) # necessarly the first element (aka the head of the queue) because it is sorted based on cost
            return best_state
        return None

