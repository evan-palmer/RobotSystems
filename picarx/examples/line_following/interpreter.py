import numpy as np


class Interpreter:
    """Interface used to interpret sensor readings."""

    def __init__(self, sensitivity: int = 1000, polarity: int = 1000) -> None:
        self.sensitivity = sensitivity
        self.polarity = polarity

    def detect_direction(self, readings: list[int], dark: bool = False) -> float:
        gradients = np.gradient(readings)
        sign_matrix = np.sign(gradients)

        print(f"Gradients: {gradients}")
        print(f"Sign Matrix: {sign_matrix}")

        return 0.0
