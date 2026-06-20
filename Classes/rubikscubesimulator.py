import time
import tkinter as tk
from tkinter import messagebox

from .cube import Cube
from .state import State
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


class RubiksCubeSimulator:
    def __init__(self):
        self.cube = Cube()

        self.window = tk.Tk()
        self.window.title("Rubik's Cube Simulator")

        # Canvas where we draw the unfolded cube (cross layout)
        # 4 faces wide x 3 faces tall = 12 x 9 stickers
        self.canvas = tk.Canvas(
            self.window,
            width=12 * TILE,
            height=9 * TILE,
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
            btn.grid(row=i // 6, column=i % 6, padx=2, pady=2)

        # Shuffle and Solve buttons on a separate frame
        action_frame = tk.Frame(self.window)
        action_frame.pack(pady=5)

        tk.Button(
            action_frame, text="Shuffle", width=10,
            command=lambda: self.actionPerformed("shuffle"),
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            action_frame, text="Solve", width=10, bg='lightgreen',
            command=lambda: self.actionPerformed("solve"),
        ).grid(row=0, column=1, padx=5)

        self.draw_cube()

    def draw_cube(self):
        """Draw the 6 faces of the cube in a cross layout."""
        self.canvas.delete("all")

        face_positions = {
            'U': (3, 0, self.cube.faceUp),
            'L': (0, 3, self.cube.faceLeft),
            'F': (3, 3, self.cube.faceFront),
            'R': (6, 3, self.cube.faceRight),
            'B': (9, 3, self.cube.faceBack),
            'D': (3, 6, self.cube.faceDown),
        }

        for col_offset, row_offset, face in face_positions.values():
            for i in range(3):
                for j in range(3):
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
        if action == ActionType.TURN_UP:      self.cube.turnUp()
        elif action == ActionType.TURN_LEFT:  self.cube.turnLeft()
        elif action == ActionType.TURN_FRONT: self.cube.turnFront()
        elif action == ActionType.TURN_RIGHT: self.cube.turnRight()
        elif action == ActionType.TURN_DOWN:  self.cube.turnDown()
        elif action == ActionType.TURN_BACK:  self.cube.turnBack()
        elif action == ActionType.RETURN_UP:      self.cube.returnUp()
        elif action == ActionType.RETURN_LEFT:    self.cube.returnLeft()
        elif action == ActionType.RETURN_FRONT:   self.cube.returnFront()
        elif action == ActionType.RETURN_RIGHT:   self.cube.returnRight()
        elif action == ActionType.RETURN_DOWN:    self.cube.returnDown()
        elif action == ActionType.RETURN_BACK:    self.cube.returnBack()

    def actionPerformed(self, action):
        """Called every time the user presses a button."""
        if action == "shuffle":
            self.cube.shuffle(10)
            self.draw_cube()
        elif action == "solve":
            self.solve()
        else:
            self.apply_action(action)
            self.draw_cube()

    def solve(self):
        """Launch A* on the current cube, then play the moves with animation."""
        if self.cube.isSolved():
            messagebox.showinfo("Solve", "The cube is already solved!")
            return

        initial_state = State(self.cube, 0, None, None)
        astar = Astar(initial_state)

        start = time.time()
        moves = astar.solve()
        elapsed = time.time() - start
        print(f"Time to solve: {elapsed:.2f}s")

        if moves is None:
            messagebox.showinfo("Solve", "No solution found.")
            return

        print(f"Solution found in {len(moves)} moves: "
              f"{[m.name for m in moves]}")
        self.play_moves(moves, 0)

    def play_moves(self, moves, index):
        """Play moves one by one with a delay so we can see the animation."""
        if index >= len(moves):
            messagebox.showinfo("Solve", f"Solved in {len(moves)} moves!")
            return
        self.apply_action(moves[index])
        self.draw_cube()
        # 500 ms delay before the next move
        self.window.after(500, lambda: self.play_moves(moves, index + 1))


def main():
    sim = RubiksCubeSimulator()
    sim.window.mainloop()


if __name__ == "__main__":
    main()
