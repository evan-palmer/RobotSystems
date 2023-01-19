import numpy as np


class Interpretation:
    """Interface used to interpret sensor readings."""

    FORWARD = 0
    LEFT = 1
    RIGHT = -1

    def __init__(self, sensitivity: int = 1000, polarity: int = 1000) -> None:
        self.sensitivity = sensitivity
        self.polarity = polarity

    def detect_direction(self, readings: list[int], dark: bool = False) -> int:
        gradients = np.gradient(readings)
        sign_matrix = np.sign(gradients)

        if dark:
            ...
        else:
            ...
