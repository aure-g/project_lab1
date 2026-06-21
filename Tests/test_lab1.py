import sys
import os
import copy
import unittest
from unittest.mock import patch

# Ensure the project root is on sys.path so package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.cube import Cube
from Classes.state import State, ACTIONS
from Classes.astar import Astar
from Classes.heuristiclabel import HeuristicLabel
from Classes.priorityqueuestate import PriorityQueueState
from Enumerations.action_type import ActionType


def make_solved_cube() -> Cube:
    """Return a Cube in its solved state (shuffle bypassed)."""
    with patch.object(Cube, 'shuffle'):
        return Cube()


# ---------------------------------------------------------------------------
# TestCube
# ---------------------------------------------------------------------------

class TestCube(unittest.TestCase):

    def setUp(self):
        self.cube = make_solved_cube()

    def test_solved_cube_has_uniform_faces(self):
        """Scenario : cube initialized not shuffled.
        Expected : each face contains 9 stickers of the same color."""
        for face in [self.cube.faceUp, self.cube.faceDown, self.cube.faceFront,
                     self.cube.faceBack, self.cube.faceLeft, self.cube.faceRight]:
            color = face[0][0]
            for row in face:
                for cell in row:
                    self.assertEqual(cell, color)

    def test_is_solved_true_on_solved(self):
        """Scenario : cube in its solved state.
        Expected : isSolved() returns True."""
        self.assertTrue(self.cube.isSolved())

    def test_is_solved_false_after_move(self):
        """Scenario : cube in its solved state to which turnUp() is applied.
        Expected : isSolved() returns False."""
        self.cube.turnUp()
        self.assertFalse(self.cube.isSolved())

    # --- identity: turn then reverse = no-op ---

    def _assert_identity(self, turn, reverse):
        original = copy.deepcopy(self.cube)
        turn()
        reverse()
        self.assertEqual(self.cube, original)

    def test_turn_up_return_up_identity(self):
        """Scenario : turnUp() followed by returnUp() on a solved cube.
        Expected : the cube returns to its initial state (reverse operation)."""
        self._assert_identity(self.cube.turnUp, self.cube.returnUp)

    def test_turn_down_return_down_identity(self):
        """Scenario : turnDown() followed by returnDown() on a solved cube.
        Expected : the cube returns to its initial state (reverse operation)."""
        self._assert_identity(self.cube.turnDown, self.cube.returnDown)

    def test_turn_front_return_front_identity(self):
        """Scenario : turnFront() followed by returnFront() on a solved cube.
        Expected : the cube returns to its initial state (reverse operation)."""
        self._assert_identity(self.cube.turnFront, self.cube.returnFront)

    def test_turn_back_return_back_identity(self):
        """Scenario : turnBack() followed by returnBack() on a solved cube.
        Expected : the cube returns to its initial state (reverse operation)."""
        self._assert_identity(self.cube.turnBack, self.cube.returnBack)

    def test_turn_left_return_left_identity(self):
        """Scenario : turnLeft() followed by returnLeft() on a solved cube.
        Expected : the cube returns to its initial state (reverse operation)."""
        self._assert_identity(self.cube.turnLeft, self.cube.returnLeft)

    def test_turn_right_return_right_identity(self):
        """Scenario : turnRight() followed by returnRight() on a solved cube.
        Expected : the cube returns to its initial state (reverse operation)."""
        self._assert_identity(self.cube.turnRight, self.cube.returnRight)

    def test_four_turns_identity(self):
        """Scenario : turnUp() applied 4 times in a row on a solved cube.
        Expected : the cube returns to its initial state (360° rotation)."""
        original = copy.deepcopy(self.cube)
        for _ in range(4):
            self.cube.turnUp()
        self.assertEqual(self.cube, original)

    def test_cube_equality(self):
        """Scenario : two independent cubes initialized without shuffling.
        Expected : __eq__ returns True (same configuration)."""
        other = make_solved_cube()
        self.assertEqual(self.cube, other)

    def test_cube_inequality_after_move(self):
        """Scenario : a solved cube compared to a copy after turnUp().
        Expected : __eq__ returns False (different configurations)."""
        other = make_solved_cube()
        other.turnUp()
        self.assertNotEqual(self.cube, other)

    # --- nouveaux tests ---

    def test_eq_with_non_cube_returns_false(self):
        """Scenario : comparison of the cube with an object that is not a Cube.
        Expected : __eq__ returns False (no error, just False)."""
        self.assertFalse(self.cube == "not a cube")
        self.assertFalse(self.cube == 42)
        self.assertFalse(self.cube == None)

    def test_deepcopy_equals_original(self):
        """Scenario : deepcopy of a solved cube.
        Expected : the copy is equal to the original (__eq__ returns True)."""
        clone = copy.deepcopy(self.cube)
        self.assertEqual(self.cube, clone)

    def test_shuffle_zero_no_change(self):
        """Scenario : shuffle(0) called on a solved cube.
        Expected : the cube remains solved (no moves applied)."""
        self.cube.shuffle(0)
        self.assertTrue(self.cube.isSolved())

    def test_str_returns_string(self):
        """Scenario : str() called on a solved cube.
        Expected : returns a non-empty string containing the face labels."""
        result = str(self.cube)
        self.assertIsInstance(result, str)
        self.assertIn('UP', result)
        self.assertIn('DOWN', result)
        self.assertIn('FRONT', result)

    def test_four_turns_identity_all_moves(self):
        """Scenario : each of the 12 moves applied 4 times in a row.
        Expected : the cube returns to its initial state (360° rotation) for each move."""
        for action, method in ACTIONS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                original = copy.deepcopy(cube)
                for _ in range(4):
                    method(cube)
                self.assertEqual(cube, original)

    def test_reverse_pair_identity_all_moves(self):
        """Scenario : for each face, returnX() followed by turnX() on a solved cube.
        Expected : the cube returns to its initial state (the opposite the other way around = identity)."""
        pairs = [
            ('returnUp',    'turnUp'),
            ('returnDown',  'turnDown'),
            ('returnFront', 'turnFront'),
            ('returnBack',  'turnBack'),
            ('returnLeft',  'turnLeft'),
            ('returnRight', 'turnRight'),
        ]
        for ccw, cw in pairs:
            with self.subTest(pair=f"{ccw}+{cw}"):
                cube = make_solved_cube()
                original = copy.deepcopy(cube)
                getattr(cube, ccw)()
                getattr(cube, cw)()
                self.assertEqual(cube, original)

    def test_turn_up_cycles_top_rows(self):
        """Scenario : turnUp() on a solved cube (Up=W, Down=Y, Front=G, Back=B, Left=O, Right=R).
        Expected : the top row of the side faces rotates — Front[0] receives Right[0],
        Right[0] receives Back[0], Back[0] receives Left[0], Left[0] receives the original Front[0]."""
        self.cube.turnUp()
        self.assertEqual(self.cube.faceFront[0], ['R', 'R', 'R'])
        self.assertEqual(self.cube.faceRight[0], ['B', 'B', 'B'])
        self.assertEqual(self.cube.faceBack[0],  ['O', 'O', 'O'])
        self.assertEqual(self.cube.faceLeft[0],  ['G', 'G', 'G'])

    def test_turn_front_cycles_border(self):
        """Scenario : turnFront() on a solved cube.
        Expected : the border around the Front face rotates — bottom row of Up receives
        the right column of Left (O), right column of Left receives top row of Down (Y),
        top row of Down receives the left column of Right (R), left column of Right
        receives the original bottom row of Up (W)."""
        self.cube.turnFront()
        self.assertEqual(self.cube.faceUp[2], ['O', 'O', 'O'])
        self.assertEqual([self.cube.faceLeft[r][2] for r in range(3)], ['Y', 'Y', 'Y'])
        self.assertEqual(self.cube.faceDown[0], ['R', 'R', 'R'])
        self.assertEqual([self.cube.faceRight[r][0] for r in range(3)], ['W', 'W', 'W'])

    def test_is_solved_false_after_each_move(self):
        """Scenario : each of the 12 moves applied alone on a solved cube.
        Expected : isSolved() returns False for each (no trivial move = no-op)."""
        for action, method in ACTIONS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                method(cube)
                self.assertFalse(cube.isSolved())


# ---------------------------------------------------------------------------
# TestHeuristicLabel
# ---------------------------------------------------------------------------

class TestHeuristicLabel(unittest.TestCase):

    def test_heuristic_zero_on_solved(self):
        """Scenario : initial state on a solved cube (valH stored in state).
        Expected : valH == 0 (all stickers are already in their target position)."""
        cube = make_solved_cube()
        state = State(cube, 0, None, None)
        self.assertEqual(state.valH, 0)

    def test_heuristic_positive_after_move(self):
        """Scenario : state after turnUp() (mixed cube by one move).
        Expected : valH > 0 (some stickers have left their target face)."""
        cube = make_solved_cube()
        cube.turnUp()
        state = State(cube, 0, None, None)
        self.assertGreater(state.valH, 0)

    def test_heuristic_admissible_1_move(self):
        """Scenario : state at exactly 1 move from the solution.
        Expected : valH <= 1 (admissibility — the heuristic never overestimates the real cost)."""
        cube = make_solved_cube()
        cube.turnUp()
        state = State(cube, 0, None, None)
        self.assertLessEqual(state.valH, 1)

    def test_heuristic_non_negative_after_any_move(self):
        """Scenario : each of the 12 moves applied alone on a solved cube.
        Expected : valH >= 0 for each state (the heuristic cannot be negative)."""
        for action, method in ACTIONS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                method(cube)
                state = State(cube, 0, None, None)
                self.assertGreaterEqual(state.valH, 0)

    def test_heuristic_positive_after_each_single_move(self):
        """Scenario : each of the 12 moves applied alone on a solved cube.
        Expected : valH > 0 for each (one move displaces at least 8 stickers)."""
        for action, method in ACTIONS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                method(cube)
                state = State(cube, 0, None, None)
                self.assertGreater(state.valH, 0)

    def test_heuristic_admissible_two_moves(self):
        """Scenario : cube mixed by exactly 2 moves (turnFront + turnRight).
        Expected : valH <= 2 (admissibility : the heuristic never overestimates the real cost)."""
        cube = make_solved_cube()
        cube.turnFront()
        cube.turnRight()
        state = State(cube, 0, None, None)
        self.assertLessEqual(state.valH, 2)

    def test_heuristic_returns_int(self):
        """Scenario : HeuristicLabel.value() called on any state.
        Expected : returns an integer (int), not a float."""
        cube = make_solved_cube()
        cube.turnUp()
        state = State(cube, 0, None, None)
        self.assertIsInstance(state.valH, int)


# ---------------------------------------------------------------------------
# TestState
# ---------------------------------------------------------------------------

class TestState(unittest.TestCase):

    def setUp(self):
        cube = make_solved_cube()
        cube.turnUp()
        self.state = State(cube, 3, None, ActionType.TURN_UP)

    def test_expand_12_children(self):
        """Scenario : expand() called on any state.
        Expected : exactly 12 child states (6 clockwise + 6 counter-clockwise)."""
        self.assertEqual(len(self.state.expand()), 12)

    def test_expand_increments_depth(self):
        """Scenario : expand() called on a state of depth 3.
        Expected : each child has nbrActions == 4 (parent depth + 1)."""
        for child in self.state.expand():
            self.assertEqual(child.nbrActions, self.state.nbrActions + 1)

    def test_expand_all_action_types_present(self):
        """Scenario : expand() called on any state.
        Expected : the 12 distinct ActionType values appear exactly once each."""
        action_types = {child.fatherAction for child in self.state.expand()}
        self.assertEqual(action_types, set(ActionType))

    def test_initial_state_stores_attributes(self):
        """Scenario : State created with explicit parameters.
        Expected : cube, nbrActions, father and fatherAction are stored as such."""
        cube = make_solved_cube()
        state = State(cube, 7, None, ActionType.TURN_LEFT)
        self.assertIs(state.cube, cube)
        self.assertEqual(state.nbrActions, 7)
        self.assertIsNone(state.father)
        self.assertEqual(state.fatherAction, ActionType.TURN_LEFT)

    def test_initial_state_none_action(self):
        """Scenario : State created with actionType=None (initial state without parent).
        Expected : fatherAction is None (no type error)."""
        cube = make_solved_cube()
        state = State(cube, 0, None, None)
        self.assertIsNone(state.fatherAction)
        self.assertIsNone(state.father)

    def test_expand_does_not_mutate_parent_cube(self):
        """Scenario : expand() called on a state.
        Expected : the parent's cube remains unchanged after expansion."""
        original_cube = copy.deepcopy(self.state.cube)
        self.state.expand()
        self.assertEqual(self.state.cube, original_cube)

    def test_expand_children_parent_reference(self):
        """Scenario : expand() called on a state.
        Expected : each child has its father attribute pointing to the parent state."""
        children = self.state.expand()
        for child in children:
            self.assertIs(child.father, self.state)

    def test_expand_children_distinct_cubes(self):
        """Scenario : expand() called on a state.
        Expected : the 12 children have distinct cube configurations."""
        children = self.state.expand()
        cube_strings = {str(child.cube) for child in children}
        self.assertEqual(len(cube_strings), 12)

    def test_expand_children_have_heuristic(self):
        """Scenario : expand() called on a state.
        Expected : each child has a calculated valH (integer >= 0)."""
        for child in self.state.expand():
            self.assertIsInstance(child.valH, int)
            self.assertGreaterEqual(child.valH, 0)


# ---------------------------------------------------------------------------
# TestPriorityQueueState
# ---------------------------------------------------------------------------

class TestPriorityQueueState(unittest.TestCase):

    def setUp(self):
        self.pq = PriorityQueueState()

    def _make_state(self, cube: Cube, nb_actions: int, valH_override: int|None = None) -> State:
        state = State(cube, nb_actions, None, ActionType.TURN_UP)
        if valH_override is not None:
            state.valH = valH_override
        return state

    def test_is_empty_initially(self):
        """Scenario : priority queue freshly instantiated.
        Expected : is_empty() returns True."""
        self.assertTrue(self.pq.is_empty())

    def test_push_not_empty(self):
        """Scenario : a state is inserted into the empty queue.
        Expected : is_empty() returns False."""
        self.pq.push(self._make_state(make_solved_cube(), 0))
        self.assertFalse(self.pq.is_empty())

    def test_pop_empty_returns_none(self):
        """Scenario : pop() called on an empty queue.
        Expected : returns None (no exception)."""
        self.assertIsNone(self.pq.pop())

    def test_push_pop_round_trip(self):
        """Scenario : push() called with a state then pop() immediately.
        Expected : the same state object is returned."""
        state = self._make_state(make_solved_cube(), 2)
        self.pq.push(state)
        self.assertIs(self.pq.pop(), state)

    def test_lowest_cost_popped_first(self):
        """Scenario : two states of different costs (10 and 2) inserted into the queue.
        Expected : pop() returns the state of cost 2 first (ascending order of f = g + h)."""
        cube_a = make_solved_cube()
        cube_b = make_solved_cube()
        cube_b.turnUp()  # different cube so no duplicate detection

        state_high = self._make_state(cube_a, 10, valH_override=0)  # cost = 10
        state_low  = self._make_state(cube_b,  2, valH_override=0)  # cost = 2

        self.pq.push(state_high)
        self.pq.push(state_low)

        self.assertIs(self.pq.pop(), state_low)

    def test_duplicate_replaced_if_lower_cost(self):
        """Scenario : same cube pushed twice, first with cost 10, then with cost 2.
        Expected : the queue contains only one state (the least costly), pop() returns the one with cost 2."""
        cube = make_solved_cube()
        state_expensive = self._make_state(cube, 10, valH_override=0)  # cost = 10
        state_cheaper   = self._make_state(cube,  2, valH_override=0)  # cost = 2, same cube

        self.pq.push(state_expensive)
        self.pq.push(state_cheaper)  # should replace state_expensive

        self.assertIs(self.pq.pop(), state_cheaper)
        self.assertTrue(self.pq.is_empty())

    def test_same_cube_higher_cost_not_replaced(self):
        """Scenario : same cube pushed twice, first with cost 2, then with cost 10.
        Expected : the second push is ignored (higher cost), pop() returns the state of cost 2."""
        cube = make_solved_cube()
        state_cheaper   = self._make_state(cube,  2, valH_override=0)  # cost = 2
        state_expensive = self._make_state(cube, 10, valH_override=0)  # cost = 10, same cube

        self.pq.push(state_cheaper)
        self.pq.push(state_expensive)  # should be ignored

        self.assertIs(self.pq.pop(), state_cheaper)
        self.assertTrue(self.pq.is_empty())

    def test_three_states_popped_in_order(self):
        """Scenario : three states of costs 5, 1 and 3 inserted into the queue.
        Expected : pop() returns them in ascending order : 1, 3, 5."""
        cube_a = make_solved_cube()
        cube_b = make_solved_cube(); cube_b.turnUp()
        cube_c = make_solved_cube(); cube_c.turnFront()

        state_5 = self._make_state(cube_a, 5, valH_override=0)
        state_1 = self._make_state(cube_b, 1, valH_override=0)
        state_3 = self._make_state(cube_c, 3, valH_override=0)

        self.pq.push(state_5)
        self.pq.push(state_1)
        self.pq.push(state_3)

        self.assertIs(self.pq.pop(), state_1)
        self.assertIs(self.pq.pop(), state_3)
        self.assertIs(self.pq.pop(), state_5)

    def test_is_empty_after_full_drain(self):
        """Scenario : two states pushed then both popped.
        Expected : is_empty() returns True once the queue is completely drained."""
        cube_a = make_solved_cube()
        cube_b = make_solved_cube(); cube_b.turnUp()

        self.pq.push(self._make_state(cube_a, 1))
        self.pq.push(self._make_state(cube_b, 2))

        self.pq.pop()
        self.pq.pop()

        self.assertTrue(self.pq.is_empty())

    def test_pop_on_empty_after_drain_returns_none(self):
        """Scenario : pop() called once too many after having drained the queue.
        Expected : returns None (no exception)."""
        self.pq.push(self._make_state(make_solved_cube(), 0))
        self.pq.pop()
        self.assertIsNone(self.pq.pop())


# ---------------------------------------------------------------------------
# TestAstar
# ---------------------------------------------------------------------------

class TestAstar(unittest.TestCase):

    def _apply_action(self, cube: Cube, action: ActionType) -> None:
        ACTIONS[action](cube)

    def test_solve_already_solved(self):
        """Scenario : A* launched on a solved cube.
        Expected : solve() returns an empty list [] (no moves needed)."""
        cube = make_solved_cube()
        moves = Astar(State(cube, 0, None, None)).solve()
        self.assertEqual(moves, [])

    def test_solve_one_move(self):
        """Scenario : A* launched on a cube mixed by a single turnUp().
        Expected : solve() returns a non-empty list (at least one move found)."""
        cube = make_solved_cube()
        cube.turnUp()
        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None
        self.assertGreater(len(moves), 0)

    def test_solve_two_moves(self):
        """Scenario : A* launched on a cube mixed by turnFront() + turnRight().
        Expected : solve() returns a non-empty solution (path found)."""
        cube = make_solved_cube()
        cube.turnFront()
        cube.turnRight()
        moves = Astar(State(cube, 0, None, None)).solve()
        self.assertIsNotNone(moves)

    def test_solution_correctness(self):
        """Scenario : cube mixed by turnUp() + turnLeft(), solved by A*.
        Expected : applying the returned moves to the mixed cube produces isSolved() == True."""
        cube = make_solved_cube()
        cube.turnUp()
        cube.turnLeft()
        test_cube = copy.deepcopy(cube)

        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None

        for action in moves:
            self._apply_action(test_cube, action)
        self.assertTrue(test_cube.isSolved())

    def test_solve_three_moves(self):
        """Scenario : A* launched on a cube mixed by turnUp() + turnFront() + turnRight().
        Expected : solve() returns a non-null solution."""
        cube = make_solved_cube()
        cube.turnUp()
        cube.turnFront()
        cube.turnRight()
        moves = Astar(State(cube, 0, None, None)).solve()
        self.assertIsNotNone(moves)

    def test_solve_optimal_for_one_move(self):
        """Scenario : A* launched on a cube mixed by exactly one turnUp().
        Expected : the optimal solution contains exactly 1 move (admissible
        + consistent heuristic → A* finds the shortest path)."""
        cube = make_solved_cube()
        cube.turnUp()
        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None
        self.assertEqual(len(moves), 1)

    def test_solve_all_12_single_moves(self):
        """Scenario : each of the 12 moves applied individually, then A* launched.
        Expected : for each move, applying the solution to the mixed cube
        produces isSolved() == True."""
        for action, method in ACTIONS.items():
            with self.subTest(action=action.name):
                cube = make_solved_cube()
                method(cube)
                test_cube = copy.deepcopy(cube)
                moves = Astar(State(cube, 0, None, None)).solve()
                assert moves is not None
                for move in moves:
                    self._apply_action(test_cube, move)
                self.assertTrue(test_cube.isSolved())

    def test_solution_is_list_of_action_types(self):
        """Scenario : A* launched on a cube mixed by a single move.
        Expected : the solution is a list whose elements are all ActionType instances."""
        cube = make_solved_cube()
        cube.turnDown()
        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None
        self.assertIsInstance(moves, list)
        for move in moves:
            self.assertIsInstance(move, ActionType)


if __name__ == '__main__':
    unittest.main()
