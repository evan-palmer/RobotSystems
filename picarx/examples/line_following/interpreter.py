import math

class Interpreter:
    """Interface used to interpret sensor readings."""

    def __init__(self, sensitivity: int = 1000, polarity: int = 1000) -> None:
        self.sensitivity = sensitivity
        self.polarity = polarity

    def detect_direction(self, readings: list[int], dark: bool = True) -> float:
        if dark:
            gradients = [readings[0] - readings[1], readings[2] - readings[1]]
        else:
            gradients = [readings[1] - readings[0], readings[1] - readings[2]]

        if abs(gradients[0] - gradients[1]) < 15:
            return 0
        else:
            if gradients[0] > gradients[1]:
                return 1
            else:
                return -1
