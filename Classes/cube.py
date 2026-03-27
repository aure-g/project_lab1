class Cube:
    def __init__(self):
        self.faceUp: list[list[str]] = [[]]
        self.faceDown: list[list[str]] = [[]]
        self.faceFront: list[list[str]] = [[]]
        self.faceBack: list[list[str]] = [[]]
        self.faceLeft: list[list[str]] = [[]]
        self.faceRight: list[list[str]] = [[]]

        COLORS = ['W', 'Y', 'R', 'O', 'G', 'B']

        NB_SQUERES: int = 9

        colors_square = []
        for color in COLORS:
            for _ in range(NB_SQUERES):
                colors_square.append(color)

        shuffle(colors_square)

        self.faceUp = [colors_square[0:3], colors_square[3:6], colors_square[6:9]]
        self.faceDown = [colors_square[9:12], colors_square[12:15], colors_square[15:18]]
        self.faceFront = [colors_square[18:21], colors_square[21:24], colors_square[24:27]]
        self.faceBack = [colors_square[27:30], colors_square[30:33], colors_square[33:36]]
        self.faceLeft = [colors_square[36:39], colors_square[39:42], colors_square[42:45]]
        self.faceRight = [colors_square[45:48], colors_square[48:51], colors_square[51:54]]


    def isSolved(self) -> bool:
        for face in [self.faceUp, self.faceDown, self.faceFront, self.faceBack, self.faceLeft, self.faceRight]:
            currentColor = face[0][0]
            for i in range(3):
                for j in range(3):
                    if face[i][j] != currentColor:
                        return False
        return True

    def __str__(self) -> str:
        #Afficher des carrés de 3x3 par face, les 6 faces sur la même ligne
        result = " UP     DOWN    FRONT    BACK   LEFT   RIGHT\n"
        for i in range(3):
            result += " ".join(self.faceUp[i]) + "   "
            result += " ".join(self.faceDown[i]) + "   "
            result += " ".join(self.faceFront[i]) + "   "
            result += " ".join(self.faceBack[i]) + "   "
            result += " ".join(self.faceLeft[i]) + "   "
            result += " ".join(self.faceRight[i]) + "\n"
        return result

    # Turn clockwise - Alexandre

    def turnUp(self) -> None:
      None
    def turnLeft(self) -> None:
      None
    def turnFront(self) -> None:
      None
    def turnRight(self) -> None:
      None
    def turnDown(self) -> None:
      None
    def turnBack(self) -> None:
      None

    # Turn counter clockwise - Aure

    def returnUp(self) -> None:
      None
    def returnLeft(self) -> None:
      None
    def returnFront(self) -> None:
      None
    def returnRight(self) -> None:
      None
    def returnDown(self) -> None:
      None
    def returnBack(self) -> None:
      None

