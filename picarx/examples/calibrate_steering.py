import os
import sys
import time

sys.path.append("..")

from picarx_improved import Picarx  # noqa


def calibrate_steering(config: str, user: str) -> None:
    """
    Calibrate the robot steering.

    Attempt to drive the robot forward for four seconds. If the robot fails to drive
    straight, then the default steering calibration should be adjusted.
    """
    car = Picarx(config, user)

    # Drive forward
    car.drive(50, 0)

    # Wait four seconds while the car is driving
    time.sleep(4)

    # Stop the car
    car.stop()


if __name__ == "__main__":
    # Disable security checks - this was written by the SunFounder folks
    user = os.popen("echo ${SUDO_USER:-$LOGNAME}").readline().strip()  # nosec
    home = os.popen(f"getent passwd {user} | cut -d: -f 6").readline().strip()  # nosec
    config = f"{home}/.config/picar-x/picar-x.conf"

    # Drive forward for a bit
    calibrate_steering(config, user)
