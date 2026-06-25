import heapq
import itertools
from .state import State

class PriorityQueueState:
    def __init__(self):
        """Initialize an empty priority queue backed by a binary heap."""
        # Heap entries are (cost, tie_breaker, state) tuples.
        # The tie_breaker is a unique increasing counter so heapq never
        # needs to compare two State objects when costs are equal.
        self.heap: list[tuple[int, int, State]] = []
        self.counter = itertools.count()
        # Tracks, per cube configuration (keyed by its string form), the
        # lowest cost currently queued. Lets push()/pop() detect duplicates
        # and stale entries in O(1) instead of scanning the whole queue.
        self.best_cost: dict[str, int] = {}

    def is_empty(self) -> bool:
        """Return True if the queue contains no states."""
        self._discard_stale_top()
        return len(self.heap) == 0

    def push(self, new_state: State) -> None:
        """Insert new_state or update it if a cheaper path to the same cube config exists."""
        cost_to_goal = new_state.valH if new_state.valH is not None else 0
        new_state_cost = new_state.nbrActions + cost_to_goal
        cube_key = str(new_state.cube)

        known_cost = self.best_cost.get(cube_key)
        if known_cost is not None and known_cost <= new_state_cost:
            # We already know an equal or cheaper path to this cube state.
            return

        # Either a brand new configuration, or a cheaper path to a known one.
        # The previous heap entry (if any) is left in place and will be
        # skipped later as a stale entry once it bubbles to the top.
        self.best_cost[cube_key] = new_state_cost
        heapq.heappush(self.heap, (new_state_cost, next(self.counter), new_state))

    def pop(self) -> State | None:
        """Remove and return the state with the lowest f-cost, or None if empty."""
        self._discard_stale_top()
        if not self.heap:
            return None
        cost, _, state = heapq.heappop(self.heap)
        del self.best_cost[str(state.cube)]
        return state

    def _discard_stale_top(self) -> None:
        """Pop superseded heap entries sitting at the top (replaced by a cheaper push)."""
        while self.heap:
            cost, _, state = self.heap[0]
            if self.best_cost.get(str(state.cube)) == cost:
                return
            heapq.heappop(self.heap)
