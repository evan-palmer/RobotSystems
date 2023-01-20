import sys
import time

sys.path.append("../..")

from control import Control
from interpreter import Interpreter
from sensor import Sensor

from picarx_improved import Picarx


def follow_line():
    sensor = Sensor("A0", "A1", "A2")
    sensor.calibrate()
    interpreter = Interpreter(polarity=True)

    while True:
        result = interpreter.detect_direction(sensor.read())
        time.sleep(0.1)


if __name__ == "__main__":
    follow_line()
