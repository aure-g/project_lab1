import random
class Cube:
    def __init__(self):
        self.faceUp: list[list[str]] = [[]]
        self.faceDown: list[list[str]] = [[]]
        self.faceFront: list[list[str]] = [[]]
        self.faceBack: list[list[str]] = [[]]
        self.faceLeft: list[list[str]] = [[]]
        self.faceRight: list[list[str]] = [[]]

        COLORS = ['W', 'Y', 'R', 'O', 'G', 'B']

        NB_SQUARES: int = 9

        colors_square = []
        for color in COLORS:
            for _ in range(NB_SQUARES):
                colors_square.append(color)

        # We begin by initializing our cube, solved
        self.faceUp = [colors_square[0:3], colors_square[3:6], colors_square[6:9]]
        self.faceDown = [colors_square[9:12], colors_square[12:15], colors_square[15:18]]
        self.faceFront = [colors_square[18:21], colors_square[21:24], colors_square[24:27]]
        self.faceBack = [colors_square[27:30], colors_square[30:33], colors_square[33:36]]
        self.faceLeft = [colors_square[36:39], colors_square[39:42], colors_square[42:45]]
        self.faceRight = [colors_square[45:48], colors_square[48:51], colors_square[51:54]]

        number_random_moves = random.randint(5,6) # can be changed depends if we give the choice to the user ?
        self.shuffle(number_random_moves)

    def isSolved(self) -> bool:
        for face in [self.faceUp, self.faceDown, self.faceFront, self.faceBack, self.faceLeft, self.faceRight]:
            currentColor = face[0][0]
            for i in range(3):
                for j in range(3):
                    if face[i][j] != currentColor:
                        return False
        return True

    def __str__(self) -> str:
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

    # For the push function in priorityqueuestate we need to compare 2 cubes
    def __eq__(self, other_cube) -> bool:
        if not isinstance(other_cube, Cube):
            return False
        return (self.faceUp == other_cube.faceUp and
                self.faceDown == other_cube.faceDown and
                self.faceFront == other_cube.faceFront and
                self.faceBack == other_cube.faceBack and
                self.faceLeft == other_cube.faceLeft and 
                self.faceRight == other_cube.faceRight)

    # Turn clockwise

    def turnUp(self) -> None:
        self.faceUp = self.turn_face(self.faceUp)

        oldFrontRow = self.faceFront[0].copy()
        self.faceFront[0] = self.faceRight[0].copy()
        self.faceRight[0] = self.faceBack[0].copy()
        self.faceBack[0] = self.faceLeft[0].copy()
        self.faceLeft[0] = oldFrontRow

    def turnDown(self) -> None:
        self.faceDown = self.turn_face(self.faceDown)

        oldFrontRow = self.faceFront[2].copy()
        self.faceFront[2] = self.faceLeft[2].copy()
        self.faceLeft[2] = self.faceBack[2].copy()
        self.faceBack[2] = self.faceRight[2].copy()
        self.faceRight[2] = oldFrontRow

    def turnFront(self) -> None:
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

    # Turn counter clockwise

    def returnUp(self) -> None:
        oldUp = [row.copy() for row in self.faceUp]
        self.faceUp = self.return_face(self.faceUp)
        
        oldFrontRow = self.faceFront[0].copy()
        self.faceFront[0] = self.faceLeft[0].copy()
        self.faceLeft[0] = self.faceBack[0].copy()
        self.faceBack[0] = self.faceRight[0].copy()
        self.faceRight[0] = oldFrontRow

    def returnDown(self) -> None:
        oldDown = [row.copy() for row in self.faceDown]
        self.faceDown = self.return_face(self.faceDown)
        
        oldFrontRow = self.faceFront[2].copy()
        self.faceFront[2] = self.faceRight[2].copy()
        self.faceRight[2] = self.faceBack[2].copy()
        self.faceBack[2] = self.faceLeft[2].copy()
        self.faceLeft[2] = oldFrontRow

    def returnFront(self) -> None:
        oldFront = [row.copy() for row in self.faceFront]
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
        oldBack = [row.copy() for row in self.faceBack]
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
        oldLeft = [row.copy() for row in self.faceLeft]
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
        oldRight = [row.copy() for row in self.faceRight]
        
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
          print(randomMove.__name__)
          randomMove()