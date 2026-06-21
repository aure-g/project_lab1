import math
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

FACE_SIZE = 3           # stickers per side of a face
ANIMATION_DELAY_MS = 500    # milliseconds between each animated move during solve playback

# Isometric projection vectors for one sticker edge (30° iso angle)
ISO_TILE = 36
_RIGHT_VEC = (ISO_TILE * math.cos(math.radians(30)), ISO_TILE * math.sin(math.radians(30)))
_LEFT_VEC = (-_RIGHT_VEC[0], _RIGHT_VEC[1])
_DOWN_VEC = (0, ISO_TILE)

# Bounding box of a single iso cube drawing, used to lay out the two cubes side by side
ISO_CUBE_WIDTH = round(6 * _RIGHT_VEC[0])
ISO_CUBE_HEIGHT = round(3 * _RIGHT_VEC[1] + 3 * _DOWN_VEC[1])

ISO_MARGIN = 55       # room around the cubes for the face-control clusters
ISO_GAP = 140          # horizontal gap between the two iso cubes (fits two facing clusters)
ISO_LABEL_HEIGHT = 24  # space reserved above each cube for its label
ARROW_OFFSET = 24      # distance from a face's outer edge to its control cluster


def _vec_add(point, vector, k=1):
    """Return point + k * vector."""
    return (point[0] + vector[0] * k, point[1] + vector[1] * k)


def _draw_sticker(canvas, p0, p1, p2, p3, color_code):
    canvas.create_polygon(*p0, *p1, *p2, *p3, fill=COLOR_MAP[color_code], outline='black', width=2)


def _draw_iso_cube(canvas, ox, oy, top_face, front_face, right_face):
    """Draw one isometric cube: top_face as the top rhombus, front_face/right_face hanging below it."""
    origin = (ox, oy)

    # Top face: row axis along _LEFT_VEC, column axis along _RIGHT_VEC
    for row in range(FACE_SIZE):
        for col in range(FACE_SIZE):
            p0 = _vec_add(_vec_add(origin, _LEFT_VEC, row), _RIGHT_VEC, col)
            p1 = _vec_add(p0, _LEFT_VEC)
            p2 = _vec_add(p1, _RIGHT_VEC)
            p3 = _vec_add(p0, _RIGHT_VEC)
            _draw_sticker(canvas, p0, p1, p2, p3, top_face[row][col])

    # Face hanging from the row=FACE_SIZE edge of the top face
    front_origin = _vec_add(origin, _LEFT_VEC, FACE_SIZE)
    for row in range(FACE_SIZE):
        for col in range(FACE_SIZE):
            p0 = _vec_add(_vec_add(front_origin, _RIGHT_VEC, col), _DOWN_VEC, row)
            p1 = _vec_add(p0, _DOWN_VEC)
            p2 = _vec_add(p1, _RIGHT_VEC)
            p3 = _vec_add(p0, _RIGHT_VEC)
            _draw_sticker(canvas, p0, p1, p2, p3, front_face[row][col])

    # Face hanging from the col=FACE_SIZE edge of the top face
    right_origin = _vec_add(origin, _RIGHT_VEC, FACE_SIZE)
    for row in range(FACE_SIZE):
        for col in range(FACE_SIZE):
            p0 = _vec_add(_vec_add(right_origin, _LEFT_VEC, col), _DOWN_VEC, row)
            p1 = _vec_add(p0, _DOWN_VEC)
            p2 = _vec_add(p1, _LEFT_VEC)
            p3 = _vec_add(p0, _LEFT_VEC)
            _draw_sticker(canvas, p0, p1, p2, p3, right_face[row][col])


def _iso_anchors(ox, oy):
    """Return the (top, front, right) anchor points for an iso cube's face-control clusters.

    Each anchor sits just outside the face's outer edge: nothing else is drawn there,
    since both hanging faces meet the top rhombus at those edges.
    """
    origin = (ox, oy)
    front_origin = _vec_add(origin, _LEFT_VEC, FACE_SIZE)
    right_origin = _vec_add(origin, _RIGHT_VEC, FACE_SIZE)

    top_anchor = (ox, oy - ARROW_OFFSET)
    front_anchor = (front_origin[0] - ARROW_OFFSET, front_origin[1] + 1.5 * ISO_TILE)
    right_anchor = (right_origin[0] + ARROW_OFFSET, right_origin[1] + 1.5 * ISO_TILE)
    return top_anchor, front_anchor, right_anchor


class RubiksCubeSimulator:
    def __init__(self):
        """Build the tkinter window, canvas, move buttons, and draw the initial cube state."""
        self.cube = Cube()

        self.window = tk.Tk()
        self.window.title("Rubik's Cube Simulator")

        self.canvas = tk.Canvas(
            self.window,
            width=2 * ISO_CUBE_WIDTH + ISO_GAP + 2 * ISO_MARGIN,
            height=ISO_LABEL_HEIGHT + ISO_MARGIN + ISO_CUBE_HEIGHT + ISO_MARGIN,
            bg='lightgray',
        )
        self.canvas.pack(padx=10, pady=10)

        # Shuffle and Solve buttons; per-face moves are triggered via clickable
        # arrows drawn next to each face on the canvas (see _add_face_controls).
        action_frame = tk.Frame(self.window)
        action_frame.pack(pady=5)

        tk.Button(
            action_frame, text="Reshuffle", width=10,
            command=lambda: self.actionPerformed("shuffle"),
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            action_frame, text="Solve", width=10,
            command=lambda: self.actionPerformed("solve"),
        ).grid(row=0, column=1, padx=5)

        self.draw_cube()

    def draw_cube(self):
        """Draw two isometric views of the cube so all 6 faces are visible in 3D."""
        self.canvas.delete("all")

        ox1 = ISO_MARGIN + ISO_CUBE_WIDTH // 2
        ox2 = ox1 + ISO_CUBE_WIDTH + ISO_GAP
        oy = ISO_LABEL_HEIGHT + ISO_MARGIN

        self.canvas.create_text(
            ox1, ISO_LABEL_HEIGHT // 2, text="Up / Front / Right", font=("Arial", 10, "bold"),
        )
        _draw_iso_cube(self.canvas, ox1, oy, self.cube.faceUp, self.cube.faceFront, self.cube.faceRight)
        top1, front1, right1 = _iso_anchors(ox1, oy)
        self._add_face_controls(top1, "UP", ActionType.TURN_UP, ActionType.RETURN_UP)
        self._add_face_controls(front1, "FRONT", ActionType.TURN_FRONT, ActionType.RETURN_FRONT)
        self._add_face_controls(right1, "RIGHT", ActionType.TURN_RIGHT, ActionType.RETURN_RIGHT)

        self.canvas.create_text(
            ox2, ISO_LABEL_HEIGHT // 2, text="Down / Back / Left", font=("Arial", 10, "bold"),
        )
        _draw_iso_cube(self.canvas, ox2, oy, self.cube.faceDown, self.cube.faceBack, self.cube.faceLeft)
        top2, front2, right2 = _iso_anchors(ox2, oy)
        self._add_face_controls(top2, "DOWN", ActionType.TURN_DOWN, ActionType.RETURN_DOWN)
        self._add_face_controls(front2, "BACK", ActionType.TURN_BACK, ActionType.RETURN_BACK)
        self._add_face_controls(right2, "LEFT", ActionType.TURN_LEFT, ActionType.RETURN_LEFT)

    def _add_face_controls(self, anchor, face_name, cw_action, ccw_action):
        """Draw a face-name label with a clockwise/counter-clockwise arrow pair below it, clickable."""
        cx, cy = anchor
        self.canvas.create_text(cx, cy - 8, text=face_name, font=("Arial", 8, "bold"))
        cw_id = self.canvas.create_text(cx - 10, cy + 8, text="↻", font=("Arial", 14, "bold"))
        ccw_id = self.canvas.create_text(cx + 10, cy + 8, text="↺", font=("Arial", 14, "bold"))

        self.canvas.tag_bind(cw_id, "<Button-1>", lambda e: self.actionPerformed(cw_action))
        self.canvas.tag_bind(ccw_id, "<Button-1>", lambda e: self.actionPerformed(ccw_action))
        for item_id in (cw_id, ccw_id):
            self.canvas.tag_bind(item_id, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item_id, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def apply_action(self, action: ActionType):
        """Apply a single move to the cube."""
        ACTIONS[action](self.cube)

    def actionPerformed(self, action):
        """Called every time the user presses a button."""
        if action == "shuffle":
            self.cube = Cube()  # restrats from a solved cub and the shuffle via the constructor
            self.draw_cube()
        elif action == "solve":
            self.solve()
        else:
            self.apply_action(action)
            self.draw_cube()

    def solve(self):
        """Launch A* in a separate thread to avoid freezing the interface."""
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
            # tkinter is not thread-safe : we switch back to the main thread via after()
            self.window.after(0, lambda: self._on_solved(moves))

        threading.Thread(target=run, daemon=True).start()

    def _on_solved(self, moves):
        """Called on the main thread once A* is done."""
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
