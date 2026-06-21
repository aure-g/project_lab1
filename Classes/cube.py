import random
class Cube:
    COLORS = ['W', 'Y', 'G', 'B', 'O', 'R']
    NB_SQUARES: int = 9
    NB_MOVE_SHUFFLE: int = 5 # A* en Python ne peut pas résoudre > 4-5 mouvements en temps raisonnable

    def __init__(self, nb_shuffle_moves: int = NB_MOVE_SHUFFLE):
        """Initialize a solved cube and scramble it with a few random moves.

        nb_shuffle_moves: number of random moves used to scramble the cube. If
        omitted, NB_MOVE_SHUFFLE is used.
        """
        self.faceUp: list[list[str]] = [[]]
        self.faceDown: list[list[str]] = [[]]
        self.faceFront: list[list[str]] = [[]]
        self.faceBack: list[list[str]] = [[]]
        self.faceLeft: list[list[str]] = [[]]
        self.faceRight: list[list[str]] = [[]]

        colors_square = []
        for color in Cube.COLORS:
            for _ in range(Cube.NB_SQUARES):
                colors_square.append(color)

        # We begin by initializing our cube, solved
        self.faceUp = [colors_square[0:3], colors_square[3:6], colors_square[6:9]]
        self.faceDown = [colors_square[9:12], colors_square[12:15], colors_square[15:18]]
        self.faceFront = [colors_square[18:21], colors_square[21:24], colors_square[24:27]]
        self.faceBack = [colors_square[27:30], colors_square[30:33], colors_square[33:36]]
        self.faceLeft = [colors_square[36:39], colors_square[39:42], colors_square[42:45]]
        self.faceRight = [colors_square[45:48], colors_square[48:51], colors_square[51:54]]

        self.shuffle(nb_shuffle_moves)

    def isSolved(self) -> bool:
        """Return True if every face is a single uniform color."""
        for face in [self.faceUp, self.faceDown, self.faceFront, self.faceBack, self.faceLeft, self.faceRight]:
            currentColor = face[0][0]
            for i in range(3):
                for j in range(3):
                    if face[i][j] != currentColor:
                        return False
        return True

    def __str__(self) -> str:
        """Return a human-readable side-by-side display of all 6 faces."""
        # Displays 3x3 squares, the 6 sides on the same line
        result = " UP     DOWN    FRONT    BACK   LEFT   RIGHT\n"
        for i in range(3):
            result += " ".join(self.faceUp[i]) + "   "
            result += " ".join(self.faceDown[i]) + "   "
            result += " ".join(self.faceFront[i]) + "   "
            result += " ".join(self.faceBack[i]) + "   "
            result += " ".join(self.faceLeft[i]) + "   "
            result += " ".join(self.faceRight[i]) + "\n"
        return result

    def __eq__(self, other_cube) -> bool:
        """Return True if both cubes have identical sticker configurations on all faces."""
        if not isinstance(other_cube, Cube):
            return False
        return (self.faceUp == other_cube.faceUp and
                self.faceDown == other_cube.faceDown and
                self.faceFront == other_cube.faceFront and
                self.faceBack == other_cube.faceBack and
                self.faceLeft == other_cube.faceLeft and 
                self.faceRight == other_cube.faceRight)

    def turnUp(self) -> None:
        """Rotate the top face 90° clockwise (U move)."""
        self.faceUp = self.turn_face(self.faceUp)

        oldFrontRow = self.faceFront[0].copy()
        self.faceFront[0] = self.faceRight[0].copy()
        self.faceRight[0] = self.faceBack[0].copy()
        self.faceBack[0] = self.faceLeft[0].copy()
        self.faceLeft[0] = oldFrontRow

    def turnDown(self) -> None:
        """Rotate the bottom face 90° clockwise (D move)."""
        self.faceDown = self.turn_face(self.faceDown)

        oldFrontRow = self.faceFront[2].copy()
        self.faceFront[2] = self.faceLeft[2].copy()
        self.faceLeft[2] = self.faceBack[2].copy()
        self.faceBack[2] = self.faceRight[2].copy()
        self.faceRight[2] = oldFrontRow

    def turnFront(self) -> None:
        """Rotate the front face 90° clockwise (F move)."""
        self.faceFront = self.turn_face(self.faceFront)

        oldUp = [self.faceUp[2][0], self.faceUp[2][1], self.faceUp[2][2]]
        
        self.faceUp[2][0] = self.faceLeft[2][2]
        self.faceUp[2][1] = self.faceLeft[1][2]
        self.faceUp[2][2] = self.faceLeft[0][2]
        
        self.faceLeft[2][2] = self.faceDown[0][0]
        self.faceLeft[1][2] = self.faceDown[0][1]
        self.faceLeft[0][2] = self.faceDown[0][2]
        
        self.faceDown[0][0] = self.faceRight[2][0]
        self.faceDown[0][1] = self.faceRight[1][0]
        self.faceDown[0][2] = self.faceRight[0][0]
        
        self.faceRight[0][0] = oldUp[0]
        self.faceRight[1][0] = oldUp[1]
        self.faceRight[2][0] = oldUp[2]

    def turnBack(self) -> None:
        """Rotate the back face 90° clockwise (B move)."""
        self.faceBack = self.turn_face(self.faceBack)

        oldUp = [self.faceUp[0][0], self.faceUp[0][1], self.faceUp[0][2]]
        
        self.faceUp[0][0] = self.faceRight[0][2]
        self.faceUp[0][1] = self.faceRight[1][2]
        self.faceUp[0][2] = self.faceRight[2][2]
        
        self.faceRight[0][2] = self.faceDown[2][2]
        self.faceRight[1][2] = self.faceDown[2][1]
        self.faceRight[2][2] = self.faceDown[2][0]
        
        self.faceDown[2][2] = self.faceLeft[2][0]
        self.faceDown[2][1] = self.faceLeft[1][0]
        self.faceDown[2][0] = self.faceLeft[0][0]
        
        self.faceLeft[0][0] = oldUp[2]
        self.faceLeft[1][0] = oldUp[1]
        self.faceLeft[2][0] = oldUp[0]

    def turnLeft(self) -> None:
        """Rotate the left face 90° clockwise (L move)."""
        self.faceLeft = self.turn_face(self.faceLeft)
        
        oldUp = [self.faceUp[0][0], self.faceUp[1][0], self.faceUp[2][0]]
        
        self.faceUp[0][0] = self.faceBack[2][2]
        self.faceUp[1][0] = self.faceBack[1][2]
        self.faceUp[2][0] = self.faceBack[0][2]
        
        self.faceBack[2][2] = self.faceDown[0][0]
        self.faceBack[1][2] = self.faceDown[1][0]
        self.faceBack[0][2] = self.faceDown[2][0]
        
        self.faceDown[0][0] = self.faceFront[0][0]
        self.faceDown[1][0] = self.faceFront[1][0]
        self.faceDown[2][0] = self.faceFront[2][0]
        
        self.faceFront[0][0] = oldUp[0]
        self.faceFront[1][0] = oldUp[1]
        self.faceFront[2][0] = oldUp[2]

    def turnRight(self) -> None:
        """Rotate the right face 90° clockwise (R move)."""
        self.faceRight = self.turn_face(self.faceRight)
        
        oldUp = [self.faceUp[0][2], self.faceUp[1][2], self.faceUp[2][2]]
        
        self.faceUp[0][2] = self.faceFront[0][2]
        self.faceUp[1][2] = self.faceFront[1][2]
        self.faceUp[2][2] = self.faceFront[2][2]
        
        self.faceFront[0][2] = self.faceDown[0][2]
        self.faceFront[1][2] = self.faceDown[1][2]
        self.faceFront[2][2] = self.faceDown[2][2]
        
        self.faceDown[0][2] = self.faceBack[2][0]
        self.faceDown[1][2] = self.faceBack[1][0]
        self.faceDown[2][2] = self.faceBack[0][0]
        
        self.faceBack[2][0] = oldUp[0]
        self.faceBack[1][0] = oldUp[1]
        self.faceBack[0][0] = oldUp[2]

    def turn_face(self, face) -> list[list[str]]:
        """Rotate a 3×3 face matrix 90° clockwise in-place and return it."""
        oldFace = [row.copy() for row in face]

        face[0][0] = oldFace[2][0]
        face[0][1] = oldFace[1][0]
        face[0][2] = oldFace[0][0]
        face[1][0] = oldFace[2][1]
        face[1][1] = oldFace[1][1]
        face[1][2] = oldFace[0][1]
        face[2][0] = oldFace[2][2]
        face[2][1] = oldFace[1][2]
        face[2][2] = oldFace[0][2]

        return face

    def returnUp(self) -> None:
        """Rotate the top face 90° counter-clockwise (U' move)."""
        self.faceUp = self.return_face(self.faceUp)
        
        oldFrontRow = self.faceFront[0].copy()
        self.faceFront[0] = self.faceLeft[0].copy()
        self.faceLeft[0] = self.faceBack[0].copy()
        self.faceBack[0] = self.faceRight[0].copy()
        self.faceRight[0] = oldFrontRow

    def returnDown(self) -> None:
        """Rotate the bottom face 90° counter-clockwise (D' move)."""
        self.faceDown = self.return_face(self.faceDown)
        
        oldFrontRow = self.faceFront[2].copy()
        self.faceFront[2] = self.faceRight[2].copy()
        self.faceRight[2] = self.faceBack[2].copy()
        self.faceBack[2] = self.faceLeft[2].copy()
        self.faceLeft[2] = oldFrontRow

    def returnFront(self) -> None:
        """Rotate the front face 90° counter-clockwise (F' move)."""
        self.faceFront = self.return_face(self.faceFront)
        
        oldUp = [self.faceUp[2][0], self.faceUp[2][1], self.faceUp[2][2]]
        
        self.faceUp[2][0] = self.faceRight[0][0]
        self.faceUp[2][1] = self.faceRight[1][0]
        self.faceUp[2][2] = self.faceRight[2][0]
        
        self.faceRight[0][0] = self.faceDown[0][2]
        self.faceRight[1][0] = self.faceDown[0][1]
        self.faceRight[2][0] = self.faceDown[0][0]
        
        self.faceDown[0][2] = self.faceLeft[2][2]
        self.faceDown[0][1] = self.faceLeft[1][2]
        self.faceDown[0][0] = self.faceLeft[0][2]
        
        self.faceLeft[2][2] = oldUp[0]
        self.faceLeft[1][2] = oldUp[1]
        self.faceLeft[0][2] = oldUp[2]

    def returnBack(self) -> None:
        """Rotate the back face 90° counter-clockwise (B' move)."""
        self.faceBack = self.return_face(self.faceBack)
        
        oldUp = [self.faceUp[0][0], self.faceUp[0][1], self.faceUp[0][2]]
        
        self.faceUp[0][2] = self.faceLeft[0][0]
        self.faceUp[0][1] = self.faceLeft[1][0]
        self.faceUp[0][0] = self.faceLeft[2][0]
        
        self.faceLeft[0][0] = self.faceDown[2][0]
        self.faceLeft[1][0] = self.faceDown[2][1]
        self.faceLeft[2][0] = self.faceDown[2][2]
        
        self.faceDown[2][0] = self.faceRight[2][2]
        self.faceDown[2][1] = self.faceRight[1][2]
        self.faceDown[2][2] = self.faceRight[0][2]
        
        self.faceRight[2][2] = oldUp[2]
        self.faceRight[1][2] = oldUp[1]
        self.faceRight[0][2] = oldUp[0]

    def returnLeft(self) -> None:
        """Rotate the left face 90° counter-clockwise (L' move)."""
        self.faceLeft = self.return_face(self.faceLeft)
        
        oldUp = [self.faceUp[0][0], self.faceUp[1][0], self.faceUp[2][0]]
        
        self.faceUp[0][0] = self.faceFront[0][0]
        self.faceUp[1][0] = self.faceFront[1][0]
        self.faceUp[2][0] = self.faceFront[2][0]
        
        self.faceFront[0][0] = self.faceDown[0][0]
        self.faceFront[1][0] = self.faceDown[1][0]
        self.faceFront[2][0] = self.faceDown[2][0]
        
        self.faceDown[0][0] = self.faceBack[2][2]
        self.faceDown[1][0] = self.faceBack[1][2]
        self.faceDown[2][0] = self.faceBack[0][2]
        
        self.faceBack[0][2] = oldUp[2]
        self.faceBack[1][2] = oldUp[1]
        self.faceBack[2][2] = oldUp[0]

    def returnRight(self) -> None:
        """Rotate the right face 90° counter-clockwise (R' move)."""
        self.faceRight = self.return_face(self.faceRight)
        
        oldUp = [self.faceUp[0][2], self.faceUp[1][2], self.faceUp[2][2]]
        
        self.faceUp[0][2] = self.faceBack[2][0]
        self.faceUp[1][2] = self.faceBack[1][0]
        self.faceUp[2][2] = self.faceBack[0][0]
        
        self.faceBack[2][0] = self.faceDown[0][2]
        self.faceBack[1][0] = self.faceDown[1][2]
        self.faceBack[0][0] = self.faceDown[2][2]
        
        self.faceDown[0][2] = self.faceFront[0][2]
        self.faceDown[1][2] = self.faceFront[1][2]
        self.faceDown[2][2] = self.faceFront[2][2]
        
        self.faceFront[0][2] = oldUp[0]
        self.faceFront[1][2] = oldUp[1]
        self.faceFront[2][2] = oldUp[2]

    def return_face(self, face) -> list[list[str]]:
        """Rotate a 3×3 face matrix 90° counter-clockwise in-place and return it."""
        oldFace = [row.copy() for row in face]

        face[0][0] = oldFace[0][2]
        face[0][1] = oldFace[1][2]
        face[0][2] = oldFace[2][2]
        face[1][0] = oldFace[0][1]
        face[1][1] = oldFace[1][1]
        face[1][2] = oldFace[2][1]
        face[2][0] = oldFace[0][0]
        face[2][1] = oldFace[1][0]
        face[2][2] = oldFace[2][0]

        return face

    def shuffle(self, nb_movements):
        """Apply nb_movements random moves to scramble the cube."""
        allActions = [self.turnUp,
                      self.turnBack,
                      self.turnRight,
                      self.turnDown,
                      self.turnLeft,
                      self.turnFront,
                      self.returnBack,
                      self.returnDown,
                      self.returnRight,
                      self.returnLeft,
                      self.returnUp,
                      self.returnFront]

        for _ in range(nb_movements):
            randomMove = random.choice(allActions)
            randomMove()