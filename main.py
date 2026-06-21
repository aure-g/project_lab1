from Classes.rubikscubesimulator import RubiksCubeSimulator


def main():
    """Launch the Rubik's Cube simulator window."""
    sim = RubiksCubeSimulator()
    sim.window.mainloop()


if __name__ == "__main__":
    main()
