import sys

sys.path.append("../..")

from picarx_improved import Picarx  # noqa


class Control:
    """Control interface used to drive the robot in a desired speed and direction."""

    def __init__(self, car: Picarx, scale: float = 100.0) -> None:
        """
        Create a new control interface.

        :param car: car to control
        :type car: Picarx
        :param scale: amount to scale the angle inputs by, defaults to 100.0
        :type scale: float, optional
        """
        self.scale = scale
        self.car = car

    def control(self, angle: float, speed: int = 50) -> None:
        """
        Drive the robot at a desired speed and angle.

        :param angle: turn angle
        :type angle: float
        :param speed: speed to drive at, defaults to 50
        :type speed: int, optional
        """
        self.car.drive(speed, angle * self.scale)
