from .state import State


class HeuristicLabel:

    @staticmethod
    def value(state: State) -> int:
        """Estimate remaining moves via Manhattan distance of stickers to their target face, divided by 8."""
        cube = state.cube

        # Target face for each color: (axis, value)
        # ex: 'W' must end up on face Up, which is the plane z = 2
        target = {
            'W': ('z', 2),  # Up
            'Y': ('z', 0),  # Down
            'G': ('y', 0),  # Front
            'B': ('y', 2),  # Back
            'O': ('x', 0),  # Left
            'R': ('x', 2),  # Right
        }

        # For each face, list the 9 stickers with their 3D position (x, y, z).
        # The cube occupies coordinates 0..2 on each axis.
        stickers = []

        # Face Up (z = 2)
        for i in range(3):
            for j in range(3):
                stickers.append((cube.faceUp[i][j], j, 2 - i, 2))

        # Face Down (z = 0)
        for i in range(3):
            for j in range(3):
                stickers.append((cube.faceDown[i][j], j, i, 0))

        # Face Front (y = 0)
        for i in range(3):
            for j in range(3):
                stickers.append((cube.faceFront[i][j], j, 0, 2 - i))

        # Face Back (y = 2)
        for i in range(3):
            for j in range(3):
                stickers.append((cube.faceBack[i][j], 2 - j, 2, 2 - i))

        # Face Left (x = 0)
        for i in range(3):
            for j in range(3):
                stickers.append((cube.faceLeft[i][j], 0, j, 2 - i))

        # Face Right (x = 2)
        for i in range(3):
            for j in range(3):
                stickers.append((cube.faceRight[i][j], 2, 2 - j, 2 - i))

        # Sum of 3D Manhattan distances from each sticker to its target face
        total = 0
        for color, x, y, z in stickers:
            axis, target_value = target[color]
            current_value = {'x': x, 'y': y, 'z': z}[axis]
            total += abs(current_value - target_value)

        # Divide by the number of stickers that change face in a single rotation
        # A rotation moves the 8 stickers of the side band to a different face.
        return total // 8
