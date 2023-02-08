import atexit
import sys
import time

sys.path.append("..")

from bus import Bus  # noqa

from picarx_improved import Picarx  # noqa

try:
    from robot_hat import ADC
except (ImportError, ModuleNotFoundError):
    print(
        "This computer does not appear to be a PiCar -X system (robot_hat is not"
        " present). Shadowing hardware calls with substitute functions."
    )
    from sim_robot_hat import ADC


class Sensor:
    """Interface used to read data from the on-board ground-scanning photosensors."""

    def __init__(
        self,
        pin_1: str = "A0",
        pin_2: str = "A1",
        pin_3: str = "A2",
    ) -> None:
        """
        Create a new interface for reading from the photosensor.

        :param bus: bus to write sensor values to
        :type bus: Bus
        :param pin_1: ADC channel 1 pin, defaults to A0
        :type pin_1: str, optional
        :param pin_2: ADC channel 2 pin, defaults to A1
        :type pin_2: str, optional
        :param pin_3: ADC channel 3 pin, defaults to A2
        :type pin_3: str, optional
        """
        self.channel_1 = ADC(pin_1)
        self.channel_2 = ADC(pin_2)
        self.channel_3 = ADC(pin_3)

        self.channel_1_trim = 0
        self.channel_2_trim = 0
        self.channel_3_trim = 0

        self.running = False
        atexit.register(self.shutdown)

    def read(self) -> list[int]:
        """
        Read the ADC values from the ground-facing photosensor.

        :return: readings from the three ADC channels
        :rtype: list[int]
        """
        return [
            max(a - b, 0)
            for a, b in zip(
                [self.channel_1.read(), self.channel_2.read(), self.channel_3.read()],
                [self.channel_1_trim, self.channel_2_trim, self.channel_3_trim],
            )
        ]

    def calibrate(self) -> None:
        """Configure the default values for each of the channels."""
        (self.channel_1_trim, self.channel_2_trim, self.channel_3_trim) = self.read()

    def produce(self, bus: Bus, delay: float = 0.05) -> None:
        """
        Poll the sensor.

        :param running: flag indicating whether or not we should be running
        :type running: bool
        :param bus: bus to write sensor values to
        :type bus: Bus
        :param delay: configure the poll frequency
        :type delay: float
        """
        self.running = True

        while self.running:
            bus.write(self.read())
            time.sleep(delay)

    def shutdown(self) -> None:
        """Exit the producer loop."""
        self.running = False


class Interpreter:
    """Interface used to interpret sensor readings."""

    def __init__(
        self,
        sensitivity: float = 0.5,
        polarity: bool = True,
    ) -> None:
        """
        Create a new interpreter to evaluate sensor readings.

        :param sensitivity: how different dark and light values are expected to be;
            should be in the range [0, 1], defaults to 0.5
        :type sensitivity: float, optional
        :param polarity: is the line dark (False) or light (True), defaults to True
        :type polarity: bool, optional
        """
        self.sensitivity = max(0, min(sensitivity, 1)) * (1 if polarity else -1)
        self.running = False
        atexit.register(self.shutdown)

    def detect_direction(self, readings: list[int], noise_thresh: int = 10) -> float:
        """
        Detect the direction of the line.

        :param readings: photosensor readings
        :type readings: list[int]
        :param noise_thresh: maximum allowable difference between gradients before
            attempting to correct the angle, defaults to 10
        :type noise_thresh: int, optional
        :return: measured direction of the line (if one exists)
        :rtype: float
        """
        # Add a bit of noise to prevent division by zero errors
        readings = [x + 1 if x == 0 else x for x in readings]
        left, middle, right = readings

        # Break early
        if abs((left - middle) - (right - middle)) < noise_thresh:
            return 0

        # Calculate the direction to turn
        if right - left > 0:
            direction = (middle - right) / (middle + right)
            direction *= -1
        else:
            direction = (middle - left) / (middle + left)

        return direction * self.sensitivity

    def produce_consume(
        self, sensor_bus: Bus, control_bus: Bus, delay: float = 0.05
    ) -> None:
        """
        Write calculated directions to the control bus using current sensor readings.

        :param sensor_bus: bus to read sensor values from
        :type sensor_bus: Bus
        :param control_bus: bus to write control signal to
        :type control_bus: Bus
        :param delay: time to wait in between read/write cycles
        :type delay: float
        """
        self.running = True

        while self.running:
            control_bus.write(self.detect_direction(sensor_bus.read()))
            time.sleep(delay)

    def shutdown(self) -> None:
        """Exit the producer-consumer loop."""
        self.running = False


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
        self.running = False
        atexit.register(self.shutdown)

    def control(self, angle: float, speed: int = 50) -> None:
        """
        Drive the robot at a desired speed and angle.

        :param angle: turn angle
        :type angle: float
        :param speed: speed to drive at, defaults to 50
        :type speed: int, optional
        """
        self.car.drive(speed, angle * self.scale)

    def consume(self, bus: Bus, delay: float = 0.05) -> None:
        """
        Control the car using the current control signal.

        :param bus: bus to read the control signal from
        :type bus: Bus
        :param delay: time to wait in between control execution
        :type delay: float
        """
        self.running = True

        while self.running:
            self.control(bus.read())
            time.sleep(delay)

    def shutdown(self) -> None:
        """Exit the consumer loop."""
        self.running = False
