import os
import time
import sys

sys.path.append("..")

from picarx_improved import Picarx


def parallel_parking(car: Picarx, direction: str, speed: float = 50) -> None:
    """
    Perform a parallel parking maneuver with the car.

    :param car: car object to interact with
    :type car: Picarx
    :param direction: direction to perform parallel parking on: left or right
    :type direction: str
    :param speed: speed to perform parking at, defaults to 50
    :type speed: float, optional
    :raises TypeError: invalid direction provided, must be either 'Left' or 'Right'
    """
    if direction not in ["Left", "Right"]:
        raise TypeError("Invalid direction provided. Options are: 'Left' and 'Right'")

    # Ensure that the speed is positive so that we drive in the correct direction
    speed = abs(speed)

    angle = -180 if direction == "Right" else 180

    # Drive forward
    car.forward(speed)
    time.sleep(1)
    car.stop()

    # Drive backward at an angle
    car.drive(-speed, angle)
    time.sleep(1)
    car.stop()

    car.drive(-speed, -angle)
    time.sleep(1)
    car.stop()

    # Realign
    car.forward(speed)
    time.sleep(1)
    car.stop()


def k_turn(car: Picarx, init_direction: str, speed: float = 50) -> None:
    """
    Perform a 3-point turn maneuver.

    This can be peformed with either an initial right turn or an initial left turn.

    :param car: car to perform the maneuver with
    :type car: Picarx
    :param init_direction: initial direction to turn: either 'Right' or 'Left'
    :type init_direction: str
    :param speed: speed to perform the maneuver at, defaults to 50
    :type speed: float, optional
    :raises TypeError: invalid initial direction provided
    """
    if init_direction not in ["Left", "Right"]:
        raise TypeError(
            "Invalid initial direction provided. Options are: 'Left' and 'Right'"
        )

    # Ensure that the speed is positive so that we drive in the correct direction
    speed = abs(speed)

    angle = 90 if init_direction == "Right" else -90

    # Drive to curb
    car.drive(speed, angle)
    time.sleep(1)
    car.stop()

    # Backup
    car.drive(-speed, -angle / 2)
    time.sleep(0.5)
    car.stop()

    # Turn to the opposite direction that we were initially facing
    car.drive(speed, -angle / 2)
    time.sleep(1)


if __name__ == "__main__":
    # Disable security checks - this was written by the SunFounder folks
    user = os.popen("echo ${SUDO_USER:-$LOGNAME}").readline().strip()  # nosec
    home = os.popen(f"getent passwd {user} | cut -d: -f 6").readline().strip()  # nosec
    config = f"{home}/.config/picar-x/picar-x.conf"

    car = Picarx(config, user)

    parallel_parking(car, "Right")
