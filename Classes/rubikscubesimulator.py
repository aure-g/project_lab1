import time
import threading
import tkinter as tk
from tkinter import messagebox

from .cube import Cube
from .state import State, ACTIONS
from .astar import Astar
from Enumerations.action_type import ActionType


# Colors used to draw each sticker
COLOR_MAP = {
    'W': 'white',
    'Y': 'yellow',
    'G': 'green',
    'B': 'blue',
    'O': 'orange',
    'R': 'red',
}

# Size of a single sticker on screen (in pixels)
TILE = 35
FACE_SIZE = 3           # stickers per side of a face
BUTTONS_PER_ROW = 6    # move buttons per row
ANIMATION_DELAY_MS = 500    # milliseconds between each animated move during solve playback


class RubiksCubeSimulator:
    def __init__(self):
        """Build the tkinter window, canvas, move buttons, and draw the initial cube state."""
        self.cube = Cube()

        self.window = tk.Tk()
        self.window.title("Rubik's Cube Simulator")

        self.canvas = tk.Canvas(
            self.window,
            width=4 * FACE_SIZE * TILE,
            height=3 * FACE_SIZE * TILE,
            bg='lightgray',
        )
        self.canvas.pack(padx=10, pady=10)

        # All buttons grouped in a frame below the canvas
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)

        # 12 move buttons, in two rows
        moves = [
            ('U',  ActionType.TURN_UP),    ('L',  ActionType.TURN_LEFT),
            ('F',  ActionType.TURN_FRONT), ('R',  ActionType.TURN_RIGHT),
            ('D',  ActionType.TURN_DOWN),  ('B',  ActionType.TURN_BACK),
            ("U'", ActionType.RETURN_UP),  ("L'", ActionType.RETURN_LEFT),
            ("F'", ActionType.RETURN_FRONT),("R'", ActionType.RETURN_RIGHT),
            ("D'", ActionType.RETURN_DOWN),("B'", ActionType.RETURN_BACK),
        ]
        for i, (label, action) in enumerate(moves):
            btn = tk.Button(
                button_frame,
                text=label,
                width=4,
                command=lambda a=action: self.actionPerformed(a),
            )
            btn.grid(row=i // BUTTONS_PER_ROW, column=i % BUTTONS_PER_ROW, padx=2, pady=2)

        # Shuffle and Solve buttons on a separate frame
        action_frame = tk.Frame(self.window)
        action_frame.pack(pady=5)

        tk.Button(
            action_frame, text="Shuffle", width=10,
            command=lambda: self.actionPerformed("shuffle"),
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            action_frame, text="Solve", width=10,
            command=lambda: self.actionPerformed("solve"),
        ).grid(row=0, column=1, padx=5)

        self.draw_cube()

    def draw_cube(self):
        """Draw the 6 faces of the cube in a cross layout."""
        self.canvas.delete("all")

        S = FACE_SIZE
        face_positions = {
            'U': (  S, 0, self.cube.faceUp),
            'L': (  0, S, self.cube.faceLeft),
            'F': (  S, S, self.cube.faceFront),
            'R': (2*S, S, self.cube.faceRight),
            'B': (3*S, S, self.cube.faceBack),
            'D': (  S, 2*S, self.cube.faceDown),
        }

        for col_offset, row_offset, face in face_positions.values():
            for i in range(FACE_SIZE):
                for j in range(FACE_SIZE):
                    x1 = (col_offset + j) * TILE
                    y1 = (row_offset + i) * TILE
                    x2 = x1 + TILE
                    y2 = y1 + TILE
                    color = COLOR_MAP[face[i][j]]
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill=color, outline='black', width=2,
                    )

    def apply_action(self, action: ActionType):
        """Apply a single move to the cube."""
        ACTIONS[action](self.cube)

    def actionPerformed(self, action):
        """Called every time the user presses a button."""
        if action == "shuffle":
            self.cube = Cube()  # repart d'un cube résolu et le mélange via le constructeur
            self.draw_cube()
        elif action == "solve":
            self.solve()
        else:
            self.apply_action(action)
            self.draw_cube()

    def solve(self):
        """Lance A* dans un thread séparé pour ne pas geler l'interface."""
        if self.cube.isSolved():
            messagebox.showinfo("Solve", "The cube is already solved!")
            return

        initial_state = State(self.cube, 0, None, None)
        solver = Astar(initial_state)

        def run():
            start = time.time()
            moves = solver.solve()
            elapsed = time.time() - start
            print(f"[Astar] Time to solve: {elapsed:.2f}s")
            # tkinter n'est pas thread-safe : on repasse sur le thread principal via after()
            self.window.after(0, lambda: self._on_solved(moves))

        threading.Thread(target=run, daemon=True).start()

    def _on_solved(self, moves):
        """Appelé sur le thread principal une fois A* terminé."""
        if moves is None:
            messagebox.showinfo("Solve", "No solution found.")
            return
        print(f"Solution found in {len(moves)} moves: {[m.name for m in moves]}")
        self.play_moves(moves, 0)

    def play_moves(self, moves, index):
        """Play moves one by one with a delay so we can see the animation."""
        if index >= len(moves):
            messagebox.showinfo("Solve", f"Solved in {len(moves)} moves!")
            return
        self.apply_action(moves[index])
        self.draw_cube()
        self.window.after(ANIMATION_DELAY_MS, lambda: self.play_moves(moves, index + 1))
