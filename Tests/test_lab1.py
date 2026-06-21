import sys
import os
import copy
import unittest
from unittest.mock import patch

# Ensure the project root is on sys.path so package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.cube import Cube
from Classes.state import State
from Classes.astar import Astar
from Classes.heuristiclabel import HeuristicLabel
from Classes.priorityqueuestate import PriorityQueueState
from Enumerations.action_type import ActionType


ACTION_METHODS: dict[ActionType, str] = {
    ActionType.TURN_UP:      'turnUp',
    ActionType.TURN_LEFT:    'turnLeft',
    ActionType.TURN_FRONT:   'turnFront',
    ActionType.TURN_RIGHT:   'turnRight',
    ActionType.TURN_DOWN:    'turnDown',
    ActionType.TURN_BACK:    'turnBack',
    ActionType.RETURN_UP:    'returnUp',
    ActionType.RETURN_LEFT:  'returnLeft',
    ActionType.RETURN_FRONT: 'returnFront',
    ActionType.RETURN_RIGHT: 'returnRight',
    ActionType.RETURN_DOWN:  'returnDown',
    ActionType.RETURN_BACK:  'returnBack',
}


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
        """Scénario : cube initialisé sans mélange.
        Attendu : chaque face contient 9 stickers de la même couleur."""
        for face in [self.cube.faceUp, self.cube.faceDown, self.cube.faceFront,
                     self.cube.faceBack, self.cube.faceLeft, self.cube.faceRight]:
            color = face[0][0]
            for row in face:
                for cell in row:
                    self.assertEqual(cell, color)

    def test_is_solved_true_on_solved(self):
        """Scénario : cube dans son état résolu.
        Attendu : isSolved() retourne True."""
        self.assertTrue(self.cube.isSolved())

    def test_is_solved_false_after_move(self):
        """Scénario : cube résolu auquel on applique turnUp().
        Attendu : isSolved() retourne False."""
        self.cube.turnUp()
        self.assertFalse(self.cube.isSolved())

    # --- identity: turn then reverse = no-op ---

    def _assert_identity(self, turn, reverse):
        original = copy.deepcopy(self.cube)
        turn()
        reverse()
        self.assertEqual(self.cube, original)

    def test_turn_up_return_up_identity(self):
        """Scénario : turnUp() suivi de returnUp() sur un cube résolu.
        Attendu : le cube revient à son état initial (opération inverse)."""
        self._assert_identity(self.cube.turnUp, self.cube.returnUp)

    def test_turn_down_return_down_identity(self):
        """Scénario : turnDown() suivi de returnDown() sur un cube résolu.
        Attendu : le cube revient à son état initial (opération inverse)."""
        self._assert_identity(self.cube.turnDown, self.cube.returnDown)

    def test_turn_front_return_front_identity(self):
        """Scénario : turnFront() suivi de returnFront() sur un cube résolu.
        Attendu : le cube revient à son état initial (opération inverse)."""
        self._assert_identity(self.cube.turnFront, self.cube.returnFront)

    def test_turn_back_return_back_identity(self):
        """Scénario : turnBack() suivi de returnBack() sur un cube résolu.
        Attendu : le cube revient à son état initial (opération inverse)."""
        self._assert_identity(self.cube.turnBack, self.cube.returnBack)

    def test_turn_left_return_left_identity(self):
        """Scénario : turnLeft() suivi de returnLeft() sur un cube résolu.
        Attendu : le cube revient à son état initial (opération inverse)."""
        self._assert_identity(self.cube.turnLeft, self.cube.returnLeft)

    def test_turn_right_return_right_identity(self):
        """Scénario : turnRight() suivi de returnRight() sur un cube résolu.
        Attendu : le cube revient à son état initial (opération inverse)."""
        self._assert_identity(self.cube.turnRight, self.cube.returnRight)

    def test_four_turns_identity(self):
        """Scénario : turnUp() appliqué 4 fois de suite sur un cube résolu.
        Attendu : le cube revient à son état initial (rotation de 360°)."""
        original = copy.deepcopy(self.cube)
        for _ in range(4):
            self.cube.turnUp()
        self.assertEqual(self.cube, original)

    def test_cube_equality(self):
        """Scénario : deux cubes indépendants initialisés sans mélange.
        Attendu : __eq__ retourne True (même configuration)."""
        other = make_solved_cube()
        self.assertEqual(self.cube, other)

    def test_cube_inequality_after_move(self):
        """Scénario : un cube résolu comparé à une copie après turnUp().
        Attendu : __eq__ retourne False (configurations différentes)."""
        other = make_solved_cube()
        other.turnUp()
        self.assertNotEqual(self.cube, other)

    # --- nouveaux tests ---

    def test_eq_with_non_cube_returns_false(self):
        """Scénario : comparaison du cube avec un objet qui n'est pas un Cube.
        Attendu : __eq__ retourne False (pas d'erreur, juste False)."""
        self.assertFalse(self.cube == "not a cube")
        self.assertFalse(self.cube == 42)
        self.assertFalse(self.cube == None)

    def test_deepcopy_equals_original(self):
        """Scénario : deepcopy d'un cube résolu.
        Attendu : la copie est égale à l'original (__eq__ True)."""
        clone = copy.deepcopy(self.cube)
        self.assertEqual(self.cube, clone)

    def test_shuffle_zero_no_change(self):
        """Scénario : shuffle(0) appelé sur un cube résolu.
        Attendu : le cube reste résolu (aucun mouvement appliqué)."""
        self.cube.shuffle(0)
        self.assertTrue(self.cube.isSolved())

    def test_str_returns_string(self):
        """Scénario : str() appelé sur un cube résolu.
        Attendu : retourne une chaîne non vide contenant les étiquettes des faces."""
        result = str(self.cube)
        self.assertIsInstance(result, str)
        self.assertIn('UP', result)
        self.assertIn('DOWN', result)
        self.assertIn('FRONT', result)

    def test_four_turns_identity_all_moves(self):
        """Scénario : chacun des 12 mouvements appliqué 4 fois de suite.
        Attendu : le cube revient à son état initial (rotation de 360°) pour chaque mouvement."""
        for action, method_name in ACTION_METHODS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                original = copy.deepcopy(cube)
                move = getattr(cube, method_name)
                for _ in range(4):
                    move()
                self.assertEqual(cube, original)

    def test_reverse_pair_identity_all_moves(self):
        """Scénario : pour chaque face, returnX() suivi de turnX() sur un cube résolu.
        Attendu : le cube revient à son état initial (l'inverse dans l'autre sens = identité)."""
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
        """Scénario : turnUp() sur un cube résolu (Up=W, Down=Y, Front=G, Back=B, Left=O, Right=R).
        Attendu : la rangée du haut des faces latérales tourne — Front[0] reçoit Right[0],
        Right[0] reçoit Back[0], Back[0] reçoit Left[0], Left[0] reçoit l'ancien Front[0]."""
        self.cube.turnUp()
        self.assertEqual(self.cube.faceFront[0], ['R', 'R', 'R'])
        self.assertEqual(self.cube.faceRight[0], ['B', 'B', 'B'])
        self.assertEqual(self.cube.faceBack[0],  ['O', 'O', 'O'])
        self.assertEqual(self.cube.faceLeft[0],  ['G', 'G', 'G'])

    def test_turn_front_cycles_border(self):
        """Scénario : turnFront() sur un cube résolu.
        Attendu : la bordure autour de la face Front tourne — rangée basse de Up reçoit
        la colonne droite de Left (O), colonne droite de Left reçoit rangée haute de Down (Y),
        rangée haute de Down reçoit la colonne gauche de Right (R), colonne gauche de Right
        reçoit l'ancienne rangée basse de Up (W)."""
        self.cube.turnFront()
        self.assertEqual(self.cube.faceUp[2], ['O', 'O', 'O'])
        self.assertEqual([self.cube.faceLeft[r][2] for r in range(3)], ['Y', 'Y', 'Y'])
        self.assertEqual(self.cube.faceDown[0], ['R', 'R', 'R'])
        self.assertEqual([self.cube.faceRight[r][0] for r in range(3)], ['W', 'W', 'W'])

    def test_is_solved_false_after_each_move(self):
        """Scénario : chacun des 12 mouvements appliqué seul sur un cube résolu.
        Attendu : isSolved() retourne False pour chacun (aucun mouvement trivial = no-op)."""
        for action, method_name in ACTION_METHODS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                getattr(cube, method_name)()
                self.assertFalse(cube.isSolved())


# ---------------------------------------------------------------------------
# TestHeuristicLabel
# ---------------------------------------------------------------------------

class TestHeuristicLabel(unittest.TestCase):

    def test_heuristic_zero_on_solved(self):
        """Scénario : état initial sur un cube résolu (valH stocké dans state).
        Attendu : valH == 0 (tous les stickers sont déjà à leur place cible)."""
        cube = make_solved_cube()
        state = State(cube, 0, None, None)
        self.assertEqual(state.valH, 0)

    def test_heuristic_positive_after_move(self):
        """Scénario : état après turnUp() (cube mélangé d'un mouvement).
        Attendu : valH > 0 (des stickers ont quitté leur face cible)."""
        cube = make_solved_cube()
        cube.turnUp()
        state = State(cube, 0, None, None)
        self.assertGreater(state.valH, 0)

    def test_heuristic_admissible_1_move(self):
        """Scénario : état à exactement 1 mouvement de la solution.
        Attendu : valH <= 1 (admissibilité — la heuristique ne surestime jamais le coût réel)."""
        cube = make_solved_cube()
        cube.turnUp()
        state = State(cube, 0, None, None)
        self.assertLessEqual(state.valH, 1)

    def test_heuristic_non_negative_after_any_move(self):
        """Scénario : chacun des 12 mouvements appliqué seul sur un cube résolu.
        Attendu : valH >= 0 pour chaque état (la heuristique ne peut pas être négative)."""
        for action, method_name in ACTION_METHODS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                getattr(cube, method_name)()
                state = State(cube, 0, None, None)
                self.assertGreaterEqual(state.valH, 0)

    def test_heuristic_positive_after_each_single_move(self):
        """Scénario : chacun des 12 mouvements appliqué seul sur un cube résolu.
        Attendu : valH > 0 pour chacun (un seul mouvement déplace au moins 8 stickers)."""
        for action, method_name in ACTION_METHODS.items():
            with self.subTest(move=action.name):
                cube = make_solved_cube()
                getattr(cube, method_name)()
                state = State(cube, 0, None, None)
                self.assertGreater(state.valH, 0)

    def test_heuristic_admissible_two_moves(self):
        """Scénario : cube mélangé par exactement 2 mouvements (turnFront + turnRight).
        Attendu : valH <= 2 (admissibilité : la heuristique ne surestime pas le coût réel)."""
        cube = make_solved_cube()
        cube.turnFront()
        cube.turnRight()
        state = State(cube, 0, None, None)
        self.assertLessEqual(state.valH, 2)

    def test_heuristic_returns_int(self):
        """Scénario : HeuristicLabel.value() appelé sur n'importe quel état.
        Attendu : retourne un entier (int), pas un float."""
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
        """Scénario : expand() appelé sur un état quelconque.
        Attendu : exactement 12 états enfants (6 clockwise + 6 counter-clockwise)."""
        self.assertEqual(len(self.state.expand()), 12)

    def test_expand_increments_depth(self):
        """Scénario : expand() appelé sur un état de profondeur 3.
        Attendu : chaque enfant a nbrActions == 4 (profondeur parent + 1)."""
        for child in self.state.expand():
            self.assertEqual(child.nbrActions, self.state.nbrActions + 1)

    def test_expand_all_action_types_present(self):
        """Scénario : expand() appelé sur un état quelconque.
        Attendu : les 12 ActionType distincts apparaissent chacun exactement une fois."""
        action_types = {child.actionPere for child in self.state.expand()}
        self.assertEqual(action_types, set(ActionType))

    def test_initial_state_stores_attributes(self):
        """Scénario : State créé avec des paramètres explicites.
        Attendu : cube, nbrActions, pere et actionPere sont stockés tels quels."""
        cube = make_solved_cube()
        state = State(cube, 7, None, ActionType.TURN_LEFT)
        self.assertIs(state.cube, cube)
        self.assertEqual(state.nbrActions, 7)
        self.assertIsNone(state.pere)
        self.assertEqual(state.actionPere, ActionType.TURN_LEFT)

    def test_initial_state_none_action(self):
        """Scénario : State créé avec actionType=None (état initial sans parent).
        Attendu : actionPere vaut None (pas d'erreur de type)."""
        cube = make_solved_cube()
        state = State(cube, 0, None, None)
        self.assertIsNone(state.actionPere)
        self.assertIsNone(state.pere)

    def test_expand_does_not_mutate_parent_cube(self):
        """Scénario : expand() appelé sur un état.
        Attendu : le cube du parent reste inchangé après l'expansion."""
        original_cube = copy.deepcopy(self.state.cube)
        self.state.expand()
        self.assertEqual(self.state.cube, original_cube)

    def test_expand_children_parent_reference(self):
        """Scénario : expand() appelé sur un état.
        Attendu : chaque enfant a son attribut pere pointant vers l'état parent."""
        children = self.state.expand()
        for child in children:
            self.assertIs(child.pere, self.state)

    def test_expand_children_distinct_cubes(self):
        """Scénario : expand() appelé sur un état.
        Attendu : les 12 enfants ont tous des configurations de cube distinctes."""
        children = self.state.expand()
        cube_strings = {str(child.cube) for child in children}
        self.assertEqual(len(cube_strings), 12)

    def test_expand_children_have_heuristic(self):
        """Scénario : expand() appelé sur un état.
        Attendu : chaque enfant possède une valH calculée (entier >= 0)."""
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
        """Scénario : file de priorité fraîchement instanciée.
        Attendu : is_empty() retourne True."""
        self.assertTrue(self.pq.is_empty())

    def test_push_not_empty(self):
        """Scénario : un état est inséré dans la file vide.
        Attendu : is_empty() retourne False."""
        self.pq.push(self._make_state(make_solved_cube(), 0))
        self.assertFalse(self.pq.is_empty())

    def test_pop_empty_returns_none(self):
        """Scénario : pop() appelé sur une file vide.
        Attendu : retourne None (pas d'exception)."""
        self.assertIsNone(self.pq.pop())

    def test_push_pop_round_trip(self):
        """Scénario : push() d'un état puis pop() immédiat.
        Attendu : le même objet état est retourné."""
        state = self._make_state(make_solved_cube(), 2)
        self.pq.push(state)
        self.assertIs(self.pq.pop(), state)

    def test_lowest_cost_popped_first(self):
        """Scénario : deux états de coûts différents (10 et 2) insérés dans la file.
        Attendu : pop() retourne l'état de coût 2 en premier (ordre croissant de f = g + h)."""
        cube_a = make_solved_cube()
        cube_b = make_solved_cube()
        cube_b.turnUp()  # different cube so no duplicate detection

        state_high = self._make_state(cube_a, 10, valH_override=0)  # cost = 10
        state_low  = self._make_state(cube_b,  2, valH_override=0)  # cost = 2

        self.pq.push(state_high)
        self.pq.push(state_low)

        self.assertIs(self.pq.pop(), state_low)

    def test_duplicate_replaced_if_lower_cost(self):
        """Scénario : même cube poussé deux fois, d'abord avec coût 10, puis coût 2.
        Attendu : la file ne contient qu'un seul état (le moins coûteux), pop() retourne celui de coût 2."""
        cube = make_solved_cube()
        state_expensive = self._make_state(cube, 10, valH_override=0)  # cost = 10
        state_cheaper   = self._make_state(cube,  2, valH_override=0)  # cost = 2, same cube

        self.pq.push(state_expensive)
        self.pq.push(state_cheaper)  # should replace state_expensive

        self.assertIs(self.pq.pop(), state_cheaper)
        self.assertTrue(self.pq.is_empty())

    def test_same_cube_higher_cost_not_replaced(self):
        """Scénario : même cube poussé deux fois, d'abord avec coût 2, puis coût 10.
        Attendu : le second push est ignoré (coût plus élevé), pop() retourne l'état de coût 2."""
        cube = make_solved_cube()
        state_cheaper   = self._make_state(cube,  2, valH_override=0)  # cost = 2
        state_expensive = self._make_state(cube, 10, valH_override=0)  # cost = 10, same cube

        self.pq.push(state_cheaper)
        self.pq.push(state_expensive)  # should be ignored

        self.assertIs(self.pq.pop(), state_cheaper)
        self.assertTrue(self.pq.is_empty())

    def test_three_states_popped_in_order(self):
        """Scénario : trois états de coûts 5, 1 et 3 insérés dans la file.
        Attendu : pop() les retourne dans l'ordre croissant : 1, 3, 5."""
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
        """Scénario : deux états poussés puis tous les deux dépilés.
        Attendu : is_empty() retourne True une fois la file entièrement vidée."""
        cube_a = make_solved_cube()
        cube_b = make_solved_cube(); cube_b.turnUp()

        self.pq.push(self._make_state(cube_a, 1))
        self.pq.push(self._make_state(cube_b, 2))

        self.pq.pop()
        self.pq.pop()

        self.assertTrue(self.pq.is_empty())

    def test_pop_on_empty_after_drain_returns_none(self):
        """Scénario : pop() appelé une fois de trop après avoir vidé la file.
        Attendu : retourne None (pas d'exception)."""
        self.pq.push(self._make_state(make_solved_cube(), 0))
        self.pq.pop()
        self.assertIsNone(self.pq.pop())


# ---------------------------------------------------------------------------
# TestAstar
# ---------------------------------------------------------------------------

class TestAstar(unittest.TestCase):

    def _apply_action(self, cube: Cube, action: ActionType) -> None:
        getattr(cube, ACTION_METHODS[action])()

    def test_solve_already_solved(self):
        """Scénario : A* lancé sur un cube déjà résolu.
        Attendu : solve() retourne une liste vide [] (aucun mouvement nécessaire)."""
        cube = make_solved_cube()
        moves = Astar(State(cube, 0, None, None)).solve()
        self.assertEqual(moves, [])

    def test_solve_one_move(self):
        """Scénario : A* lancé sur un cube mélangé par un seul turnUp().
        Attendu : solve() retourne une liste non vide (au moins un mouvement trouvé)."""
        cube = make_solved_cube()
        cube.turnUp()
        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None
        self.assertGreater(len(moves), 0)

    def test_solve_two_moves(self):
        """Scénario : A* lancé sur un cube mélangé par turnFront() + turnRight().
        Attendu : solve() retourne une solution non None (chemin trouvé)."""
        cube = make_solved_cube()
        cube.turnFront()
        cube.turnRight()
        moves = Astar(State(cube, 0, None, None)).solve()
        self.assertIsNotNone(moves)

    def test_solution_correctness(self):
        """Scénario : cube mélangé par turnUp() + turnLeft(), résolu par A*.
        Attendu : appliquer les moves retournés sur le cube mélangé produit isSolved() == True."""
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
        """Scénario : A* lancé sur un cube mélangé par turnUp() + turnFront() + turnRight().
        Attendu : solve() retourne une solution non None."""
        cube = make_solved_cube()
        cube.turnUp()
        cube.turnFront()
        cube.turnRight()
        moves = Astar(State(cube, 0, None, None)).solve()
        self.assertIsNotNone(moves)

    def test_solve_optimal_for_one_move(self):
        """Scénario : A* lancé sur un cube mélangé par exactement un turnUp().
        Attendu : la solution optimale fait exactement 1 mouvement (heuristique admissible
        + consistante → A* trouve le plus court chemin)."""
        cube = make_solved_cube()
        cube.turnUp()
        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None
        self.assertEqual(len(moves), 1)

    def test_solve_all_12_single_moves(self):
        """Scénario : chacun des 12 mouvements appliqué seul, puis A* lancé.
        Attendu : pour chaque mouvement, appliquer la solution au cube mélangé
        produit isSolved() == True."""
        for action, method_name in ACTION_METHODS.items():
            with self.subTest(action=action.name):
                cube = make_solved_cube()
                getattr(cube, method_name)()
                test_cube = copy.deepcopy(cube)
                moves = Astar(State(cube, 0, None, None)).solve()
                assert moves is not None
                for move in moves:
                    self._apply_action(test_cube, move)
                self.assertTrue(test_cube.isSolved())

    def test_solution_is_list_of_action_types(self):
        """Scénario : A* lancé sur un cube mélangé d'un mouvement.
        Attendu : la solution est une list dont chaque élément est un ActionType."""
        cube = make_solved_cube()
        cube.turnDown()
        moves = Astar(State(cube, 0, None, None)).solve()
        assert moves is not None
        self.assertIsInstance(moves, list)
        for move in moves:
            self.assertIsInstance(move, ActionType)


if __name__ == '__main__':
    unittest.main()
