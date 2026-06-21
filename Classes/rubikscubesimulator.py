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

# Isometric projection: elevation angle of the horizontal-plane edges (the vertical
# edges always stay vertical). Both cubes use the same angle/proportions; only the
# orientation differs. `flip=True` draws the anchor face at the BOTTOM of the
# silhouette (apex pointing down, the two side faces hanging upward from it) instead
# of at the top, giving a "viewed from below" look with identical proportions.
ISO_TILE = 36
ISO_ANGLE = 30


def _iso_vectors(angle_deg, flip=False):
    """Return (right_vec, left_vec, down_vec) for one sticker edge at the given elevation angle."""
    right_vec = (ISO_TILE * math.cos(math.radians(angle_deg)), ISO_TILE * math.sin(math.radians(angle_deg)))
    down_vec = (0, ISO_TILE)
    if flip:
        right_vec = (right_vec[0], -right_vec[1])
        down_vec = (0, -ISO_TILE)
    left_vec = (-right_vec[0], right_vec[1])
    return right_vec, left_vec, down_vec


def _iso_cube_size(right_vec, down_vec):
    """Return the (width, height) bounding box of an iso cube drawn with these vectors."""
    width = round(6 * right_vec[0])
    height = round(3 * abs(right_vec[1]) + 3 * abs(down_vec[1]))
    return width, height


ISO_MARGIN = 55       # room around the cubes for the face-control clusters
ISO_GAP = 140          # horizontal gap between the two iso cubes (fits two facing clusters)
ISO_LABEL_HEIGHT = 24  # space reserved above each cube for its label
ARROW_OFFSET = 24      # distance from a face's outer edge to its control cluster


def _vec_add(point, vector, k=1):
    """Return point + k * vector."""
    return (point[0] + vector[0] * k, point[1] + vector[1] * k)


def _draw_sticker(canvas, p0, p1, p2, p3, color_code):
    canvas.create_polygon(*p0, *p1, *p2, *p3, fill=COLOR_MAP[color_code], outline='black', width=2)


def _draw_iso_cube(canvas, ox, oy, top_face, front_face, right_face, right_vec, left_vec, down_vec, flip=False):
    """Draw one isometric cube: top_face as the anchor rhombus, front_face/right_face hanging from it.

    Cube's own convention, going clockwise Front->Right->Back->Left->Front: every side
    face's row 0 is adjacent to Up, row 2 to Down; its col 0 is adjacent to its counter-
    clockwise neighbor, col 2 to its clockwise neighbor. The drawing always has the
    hanging faces' row 0 touching the anchor rhombus and the right-hanging face's col 0
    touching the rhombus (col 2 touching the front-hanging face). So:
    - when the anchor is Down (flip=True), the row order of both hanging faces must be
      reversed, otherwise the Up-adjacent row (changed by U turns) is drawn next to Down;
    - the right-hanging face's column order must ALWAYS be reversed, since its col 0
      (its counter-clockwise neighbor, e.g. Front for the Right face) needs to touch the
      front-hanging face, not the open margin;
    - the anchor rhombus's own column order must be reversed too when flip=True, so its
      column adjacent to the right-hanging face's content lines up with that edge.
    """
    origin = (ox, oy)

    # Top face: row axis along left_vec, column axis along right_vec
    for row in range(FACE_SIZE):
        for col in range(FACE_SIZE):
            p0 = _vec_add(_vec_add(origin, left_vec, row), right_vec, col)
            p1 = _vec_add(p0, left_vec)
            p2 = _vec_add(p1, right_vec)
            p3 = _vec_add(p0, right_vec)
            face_col = FACE_SIZE - 1 - col if flip else col
            _draw_sticker(canvas, p0, p1, p2, p3, top_face[row][face_col])

    # Face hanging from the row=FACE_SIZE edge of the top face
    front_origin = _vec_add(origin, left_vec, FACE_SIZE)
    for row in range(FACE_SIZE):
        for col in range(FACE_SIZE):
            p0 = _vec_add(_vec_add(front_origin, right_vec, col), down_vec, row)
            p1 = _vec_add(p0, down_vec)
            p2 = _vec_add(p1, right_vec)
            p3 = _vec_add(p0, right_vec)
            face_row = FACE_SIZE - 1 - row if flip else row
            _draw_sticker(canvas, p0, p1, p2, p3, front_face[face_row][col])

    # Face hanging from the col=FACE_SIZE edge of the top face
    right_origin = _vec_add(origin, right_vec, FACE_SIZE)
    for row in range(FACE_SIZE):
        for col in range(FACE_SIZE):
            p0 = _vec_add(_vec_add(right_origin, left_vec, col), down_vec, row)
            p1 = _vec_add(p0, down_vec)
            p2 = _vec_add(p1, left_vec)
            p3 = _vec_add(p0, left_vec)
            face_row = FACE_SIZE - 1 - row if flip else row
            face_col = FACE_SIZE - 1 - col
            _draw_sticker(canvas, p0, p1, p2, p3, right_face[face_row][face_col])


def _iso_anchors(ox, oy, right_vec, left_vec, down_vec):
    """Return the (top, front, right) anchor points for an iso cube's face-control clusters.

    Each anchor sits just outside the face's outer edge: nothing else is drawn there,
    since both hanging faces meet the anchor rhombus at those edges.
    """
    origin = (ox, oy)
    front_origin = _vec_add(origin, left_vec, FACE_SIZE)
    right_origin = _vec_add(origin, right_vec, FACE_SIZE)

    # The rhombus extends toward increasing right_vec[1]; its free side is the opposite way.
    outward_sign = 1 if right_vec[1] >= 0 else -1
    top_anchor = (ox, oy - ARROW_OFFSET * outward_sign)
    front_anchor = (front_origin[0] - ARROW_OFFSET, front_origin[1] + 1.5 * down_vec[1])
    right_anchor = (right_origin[0] + ARROW_OFFSET, right_origin[1] + 1.5 * down_vec[1])
    return top_anchor, front_anchor, right_anchor


class RubiksCubeSimulator:
    def __init__(self):
        """Build the tkinter window, canvas, move buttons, and draw the initial cube state."""
        self.cube = Cube()

        # Up/Front/Right cube has its anchor face on top. Down/Back/Left uses the same
        # angle/proportions, just flipped so the anchor face sits at the bottom instead.
        self.vec1 = _iso_vectors(ISO_ANGLE)
        self.vec2 = _iso_vectors(ISO_ANGLE, flip=True)
        self.size1 = _iso_cube_size(self.vec1[0], self.vec1[2])
        self.size2 = _iso_cube_size(self.vec2[0], self.vec2[2])
        self.area_height = max(self.size1[1], self.size2[1])

        self.window = tk.Tk()
        self.window.title("Rubik's Cube Simulator")

        self.canvas = tk.Canvas(
            self.window,
            width=2 * ISO_MARGIN + self.size1[0] + ISO_GAP + self.size2[0],
            height=ISO_LABEL_HEIGHT + ISO_MARGIN + self.area_height + ISO_MARGIN,
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
            action_frame, text="Reset", width=10,
            command=lambda: self.actionPerformed("reset"),
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            action_frame, text="Solve", width=10,
            command=lambda: self.actionPerformed("solve"),
        ).grid(row=0, column=2, padx=5)

        self.draw_cube()

    def draw_cube(self):
        """Draw two isometric views of the cube so all 6 faces are visible in 3D."""
        self.canvas.delete("all")

        ox1 = ISO_MARGIN + self.size1[0] // 2
        ox2 = ISO_MARGIN + self.size1[0] + ISO_GAP + self.size2[0] // 2
        # Both cubes share a bottom baseline: cube 1's apex sits on top of its own
        # height, cube 2's apex (flipped, at the bottom) sits right on the baseline.
        y_bottom = ISO_LABEL_HEIGHT + ISO_MARGIN + self.area_height
        oy1 = y_bottom - self.size1[1]
        oy2 = y_bottom

        self.canvas.create_text(
            ox1, ISO_LABEL_HEIGHT // 2, text="Up / Front / Right", font=("Arial", 10, "bold"),
        )
        _draw_iso_cube(self.canvas, ox1, oy1, self.cube.faceUp, self.cube.faceFront, self.cube.faceRight, *self.vec1)
        top1, front1, right1 = _iso_anchors(ox1, oy1, *self.vec1)
        self._add_face_controls(top1, "UP", ActionType.TURN_UP, ActionType.RETURN_UP)
        self._add_face_controls(front1, "FRONT", ActionType.TURN_FRONT, ActionType.RETURN_FRONT)
        self._add_face_controls(right1, "RIGHT", ActionType.TURN_RIGHT, ActionType.RETURN_RIGHT)

        self.canvas.create_text(
            ox2, ISO_LABEL_HEIGHT // 2, text="Down / Back / Left", font=("Arial", 10, "bold"),
        )
        _draw_iso_cube(
            self.canvas, ox2, oy2, self.cube.faceDown, self.cube.faceBack, self.cube.faceLeft, *self.vec2, flip=True,
        )
        top2, front2, right2 = _iso_anchors(ox2, oy2, *self.vec2)
        self._add_face_controls(top2, "DOWN", ActionType.TURN_DOWN, ActionType.RETURN_DOWN)
        self._add_face_controls(front2, "BACK", ActionType.TURN_BACK, ActionType.RETURN_BACK)
        self._add_face_controls(right2, "LEFT", ActionType.TURN_LEFT, ActionType.RETURN_LEFT)

    def _add_face_controls(self, anchor, face_name, cw_action, ccw_action):
        """Draw a face-name label with a clockwise/counter-clockwise arrow pair below it, clickable."""
        cx, cy = anchor
        self.canvas.create_text(cx, cy - 8, text=face_name, font=("Arial", 8, "bold"))
        cw_id = self.canvas.create_text(cx - 10, cy + 8, text="↻", font=("Segoe UI Symbol", 14, "bold"))
        ccw_id = self.canvas.create_text(cx + 10, cy + 8, text="↺", font=("Segoe UI Symbol", 14, "bold"))

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
            self.cube.shuffle(Cube.NB_MOVE_SHUFFLE)
            self.draw_cube()
        elif action == "reset":
            self.cube.reset()
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
