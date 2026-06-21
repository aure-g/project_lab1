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
    """Mélange un cube avec Cube.NB_MOVE_SHUFFLE mouvements, le résout avec A*,
    et dépose (run_index, temps écoulé) dans result_queue. Module-level pour
    être picklable par multiprocessing (nécessaire pour exécuter les essais
    en parallèle). Si le processus est tué pour timeout, rien n'est déposé."""
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
        """Lance les NB_RUNS résolutions en parallèle (un processus par essai).
        Un budget total de MAX_SOLVE_SECONDS est partagé entre tous les essais :
        à l'échéance, tout processus encore actif est tué (résultat = None) au
        lieu d'attendre sa fin naturelle, pour borner la durée de la suite."""
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
            print(f"[performance] essai {i}/{NB_RUNS} (NB_MOVE_SHUFFLE={Cube.NB_MOVE_SHUFFLE}) -> {label}")

    def assert_completed_in_time(self, run_index: int):
        elapsed = self.results[run_index]
        if elapsed is None:
            self.fail(f"essai {run_index + 1} n'a pas terminé en moins de {MAX_SOLVE_SECONDS}s")
        self.assertLess(elapsed, MAX_SOLVE_SECONDS)


def _make_test_solve_time(run_index: int):
    """Crée une méthode de test pour l'essai run_index (0-based)."""
    def test(self: TestAstarPerformance):
        self.assert_completed_in_time(run_index)
    test.__doc__ = (
        f"Scénario : cube mélangé avec Cube.NB_MOVE_SHUFFLE mouvements (essai {run_index + 1}/{NB_RUNS}).\n"
        f"        Attendu : A* trouve une solution en moins de MAX_SOLVE_SECONDS."
    )
    return test


for _i in range(NB_RUNS):
    setattr(TestAstarPerformance, f"test_solve_time_default_scramble_{_i + 1}", _make_test_solve_time(_i))
del _i


if __name__ == '__main__':
    unittest.main()
