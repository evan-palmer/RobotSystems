from picarx_improved import Picarx


class Sensor:
    """Sensor class used to get ultrasonic sensor readings."""

    def __init__(self, car: Picarx) -> None:
        """
        Create a new ultrasonic sensor reader.

        :param car: car instance
        :type car: Picarx
        """
        self.car = car

    def read(self) -> float:
        """
        Get the ultrasonic sensor reading.

        :return: distance
        :rtype: float
        """
        return max(self.car.get_distance(), 0)


class Interpreter:
    """Interprets sensor readings obtained from the ultrasonic sensor for control."""

    def __init__(self, min_distance: float) -> None:
        """
        Create a new ultrasonic sensor reading interpreter.

        :param min_distance: minimum distance to an obstace before stopping.
        :type min_distance: float
        """
        self.min_distance = min_distance

    def calculate_speed(self, distance: float) -> float:
        """
        Calculate a scalar to apply to the current driving speed.

        :param distance: distance to an obstacle
        :type distance: float
        :return: 0 if too close to an obstacle, 1 otherwise
        :rtype: float
        """
        return 0 if distance < self.min_distance else 1


class Control:
    """Controls the speed of the robot."""

    def __init__(self, car: Picarx, speed: float) -> None:
        """
        Create a new speed controller.

        :param car: car instance to control
        :type car: Picarx
        :param speed: speed the car should drive at
        :type speed: float
        """
        self.speed = speed
        self.car = car

    def control(self, speed_scalar: float) -> None:
        """
        Control the speed of the car.

        :param speed_scalar: scalar value to apply to the desired speed
        :type speed_scalar: float
        """
        self.car.drive(self.speed * speed_scalar)
