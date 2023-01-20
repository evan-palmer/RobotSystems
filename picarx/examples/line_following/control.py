import sys

sys.path.append("../..")

from picarx_improved import Picarx

class Control:
    """Controller designed to drive the robot toward and along an identified line."""

    def __init__(self, car: Picarx, scale: float = 100.0) -> None:
        self.scale = scale
        self.car = car

    def control(self, angle: float, speed: int = 50) -> None:
        # print(angle * self.scale)
        self.car.drive(speed, angle * self.scale)


    
