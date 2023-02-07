import sys

sys.path.append("..")

try:
    from robot_hat import ADC
except (ImportError, ModuleNotFoundError):
    print(
        "This computer does not appear to be a PiCar -X system (robot_hat is not"
        " present). Shadowing hardware calls with substitute functions."
    )
    from sim_robot_hat import ADC

from picarx_improved import Picarx
from rossros import Bus, Consumer, ConsumerProducer, Producer


class Sensor:
    """Interface used to read data from the on-board ground-scanning photosensors."""

    def __init__(
        self,
        io_bus: Bus,
        termination_bus: Bus,
        pin_1: str = "A0",
        pin_2: str = "A1",
        pin_3: str = "A2",
        delay: float = 0.05,
    ) -> None:
        self.channel_1 = ADC(pin_1)
        self.channel_2 = ADC(pin_2)
        self.channel_3 = ADC(pin_3)

        self.channel_1_trim = 0
        self.channel_2_trim = 0
        self.channel_3_trim = 0

        self.producer = Producer(
            self.read,
            io_bus,
            termination_bus=termination_bus,
            name="PhotosensorSensor",
            delay=delay,
        )

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

    def start(self) -> None:
        self.producer()


class Interpreter:
    """Interface used to interpret sensor readings."""

    def __init__(
        self,
        sensor_bus: Bus,
        control_bus: Bus,
        termination_bus: Bus,
        sensitivity: float = 0.5,
        polarity: bool = True,
        delay: float = 0.05,
    ) -> None:
        self.sensitivity = max(0, min(sensitivity, 1)) * (1 if polarity else -1)
        self.consumer_producer = ConsumerProducer(
            self.detect_direction,
            sensor_bus,
            control_bus,
            termination_bus=termination_bus,
            name="PhotosensorInterpreter",
            delay=delay,
        )

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

    def start(self) -> None:
        self.consumer_producer()


class Control:
    """Control interface used to drive the robot in a desired speed and direction."""

    def __init__(
        self, bus: Bus, car: Picarx, scale: float = 100.0, delay: float = 0.05
    ) -> None:
        """
        Create a new control interface.

        :param bus: bus to read control signal from
        :type bus: Bus
        :param car: car to control
        :type car: Picarx
        :param scale: amount to scale the angle inputs by, defaults to 100.0
        :type scale: float, optional
        :param delay: time to delay between control signal readings, defaults to 0.1
        :type delay: float, optional
        """
        self.scale = scale
        self.car = car

        self.consumer = Consumer()

    def control(self, angle: float, speed: int = 50) -> None:
        """
        Drive the robot at a desired speed and angle.

        :param angle: turn angle
        :type angle: float
        :param speed: speed to drive at, defaults to 50
        :type speed: int, optional
        """
        self.car.drive(speed, angle * self.scale)

    def consume(self, bus: Bus, delay: float) -> None:
        """
        Control the car using the current control signal.

        :param bus: bus to read the control signal from
        :type bus: Bus
        :param delay: time to wait in between control execution
        :type delay: float
        """
        while self.running:
            self.control(bus.read())
            time.sleep(delay)

    def start(self) -> None:
        """Start the control thread."""
        self.running = True
        self._consumer_thread.start()

    def stop(self) -> None:
        """Stop the controller."""
        self.running = False
        self._consumer_thread.join()


def follow_line(config: str, user: str, scale: float = 50.0):
    """
    Follow a line using the Picarx.

    :param config: picarx config file
    :type config: str
    :param user: config file owner
    :type user: str
    :param scale: amount to scale angles by, defaults to 50.0
    :type scale: float, optional
    """
    sensor_bus = Bus()
    control_bus = Bus()

    sensor = Sensor(sensor_bus)

    input("Press 'enter' to calibrate the sensor")

    sensor.calibrate()

    interpreter = Interpreter(sensor_bus, control_bus, polarity=True)
    car = Picarx(config, user)
    controller = Control(control_bus, car, scale)

    input("Press 'enter' to start line following")

    sensor.start()
    interpreter.start()
    controller.start()

    while True:
        ...


if __name__ == "__main__":
    # Disable security checks - this was written by the SunFounder folks
    user = os.popen("echo ${SUDO_USER:-$LOGNAME}").readline().strip()  # nosec
    home = os.popen(f"getent passwd {user} | cut -d: -f 6").readline().strip()  # nosec
    config = f"{home}/.config/picar-x/picar-x.conf"

    follow_line(config, user)
