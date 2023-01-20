import os
import sys
import time

sys.path.append("../..")

from control import Control
from interpreter import Interpreter
from sensor import Sensor

from picarx_improved import Picarx


def follow_line(config: str, user: str, scale: float = 50.0):
    sensor = Sensor()
    interpreter = Interpreter(polarity=True)
    car = Picarx(config, user)
    controller = Control(car, scale)

    input("Press 'enter' to calibrate")
    
    # Calibrate the sensors
    sensor.calibrate()

    input("Press 'enter' to start line following")

    while True:
        controller.control(interpreter.detect_direction(sensor.read()))
        time.sleep(0.1)


if __name__ == "__main__":
    # Disable security checks - this was written by the SunFounder folks
    user = os.popen("echo ${SUDO_USER:-$LOGNAME}").readline().strip()  # nosec
    home = os.popen(f"getent passwd {user} | cut -d: -f 6").readline().strip()  # nosec
    config = f"{home}/.config/picar-x/picar-x.conf"

    follow_line(config, user)
