import os
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
from bus import Bus  # noqa
from photosensor import Control, Interpreter, Sensor  # noqa

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
    # Instantiate the buses
    sensor_bus = Bus()
    control_bus = Bus()

    # Construct our fun new tools
    sensor = Sensor()
    interpreter = Interpreter(polarity=True)
    car = Picarx(config, user)
    controller = Control(car, scale)

    input("Press 'enter' to calibrate the sensor")

    sensor.calibrate()

    input("Press 'enter' to start line following")

    tp = ThreadPoolExecutor(max_workers=3)

    tp.submit(sensor.produce, sensor_bus)
    tp.submit(interpreter.produce_consume, sensor_bus, control_bus)
    tp.submit(controller.consume, control_bus)

    input("Press 'enter' to quit")

    sensor.shutdown()
    interpreter.shutdown()
    controller.shutdown()
    tp.shutdown()


if __name__ == "__main__":
    # Disable security checks - this was written by the SunFounder folks
    user = os.popen("echo ${SUDO_USER:-$LOGNAME}").readline().strip()  # nosec
    home = os.popen(f"getent passwd {user} | cut -d: -f 6").readline().strip()  # nosec
    config = f"{home}/.config/picar-x/picar-x.conf"

    follow_line(config, user)