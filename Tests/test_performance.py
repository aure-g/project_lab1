import sys
import os
import time
import unittest
import multiprocessing

# Ensure the project root is on sys.path so package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.cube import Cube
from Classes.state import State
from Classes.astar import Astar

NB_RUNS = 10
MAX_SOLVE_SECONDS = 120.0


def _solve_with_default_scramble(run_index: int, result_queue: multiprocessing.Queue) -> None:
    """Shuffle a cube with Cube.NB_MOVE_SHUFFLE moves, solve it with A*,
    and deposit (run_index, elapsed time) in result_queue. Module-level for
    being picklable by multiprocessing (necessary for running tests
    in parallel). If the process is killed for timeout, nothing is deposited."""
    cube = Cube(Cube.NB_MOVE_SHUFFLE)
    start = time.perf_counter()
    moves = Astar(State(cube, 0, None, None)).solve()
    elapsed = time.perf_counter() - start
    assert moves is not None
    result_queue.put((run_index, elapsed))


# ---------------------------------------------------------------------------
# TestAstarPerformance
# ---------------------------------------------------------------------------

class TestAstarPerformance(unittest.TestCase):

    results: list[float | None] = []

    @classmethod
    def setUpClass(cls):
        """Launches the NB_RUNS resolutions in parallel (one process per trial).
        A total budget of MAX_SOLVE_SECONDS is shared between all trials :
        at the deadline, any active process is killed (result = None) instead of
        waiting for its natural end, to bound the duration of the suite."""
        result_queue: multiprocessing.Queue = multiprocessing.Queue()
        processes = [
            multiprocessing.Process(target=_solve_with_default_scramble, args=(i, result_queue))
            for i in range(NB_RUNS)
        ]
        for p in processes:
            p.start()

        deadline = time.perf_counter() + MAX_SOLVE_SECONDS
        for p in processes:
            remaining = max(0.0, deadline - time.perf_counter())
            p.join(remaining)
            if p.is_alive():
                p.terminate()
                p.join()

        collected: dict[int, float] = {}
        while not result_queue.empty():
            run_index, elapsed = result_queue.get()
            collected[run_index] = elapsed

        cls.results = [collected.get(i) for i in range(NB_RUNS)]

        for i, elapsed in enumerate(cls.results, start=1):
            label = f"{elapsed:.3f}s" if elapsed is not None else f"TIMEOUT/ECHEC (> {MAX_SOLVE_SECONDS}s)"
            print(f"[performance] try {i}/{NB_RUNS} (NB_MOVE_SHUFFLE={Cube.NB_MOVE_SHUFFLE}) -> {label}")

    def assert_completed_in_time(self, run_index: int):
        elapsed = self.results[run_index]
        if elapsed is None:
            self.fail(f"try {run_index + 1} did not complete within {MAX_SOLVE_SECONDS}s")
        self.assertLess(elapsed, MAX_SOLVE_SECONDS)


def _make_test_solve_time(run_index: int):
    """Creates a test method for the trial run_index (0-based)."""
    def test(self: TestAstarPerformance):
        self.assert_completed_in_time(run_index)
    test.__doc__ = (
        f"Scenario : cube mixed with Cube.NB_MOVE_SHUFFLE moves (try {run_index + 1}/{NB_RUNS}).\n"
        f"        Expected : A* finds a solution in less than MAX_SOLVE_SECONDS."
    )
    return test


for _i in range(NB_RUNS):
    setattr(TestAstarPerformance, f"test_solve_time_default_scramble_{_i + 1}", _make_test_solve_time(_i))
del _i


if __name__ == '__main__':
    unittest.main()
