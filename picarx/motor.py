import atexit
import time

try:
    from robot_hat import PWM, Pin
    from robot_hat.utils import reset_mcu

    reset_mcu()
    time.sleep(0.2)
except (ImportError, ModuleNotFoundError):
    print(
        "This computer does not appear to be a PiCar -X system (robot_hat is not"
        " present). Shadowing hardware calls with substitute functions."
    )
    from sim_robot_hat import PWM, Pin


class Motor:
    """Interface used to interact with the robot motors."""

    PERIOD = 4095
    PRESCALER = 10

    def __init__(
        self,
        direction_pin: Pin,
        pwm_pin: PWM,
        default_direction: int = 1,
        trim: int = 0,
    ) -> None:
        """
        Create a new motor interface.

        :param direction_pin: pin used to set the motor direction
        :type direction_pin: Pin
        :param pwm_pin: pin used to set the motor PWM value
        :type pwm_pin: PWM
        :param default_direction: default motor direction, defaults to 1
        :type default_direction: int, optional
        :param trim: motor trim value, defaults to 0
        :type trim: int, optional
        """
        self.direction_pin = direction_pin
        self.pwm_pin = pwm_pin
        self.direction = default_direction
        self.trim = trim

        # Configure the PWM signal
        pwm_pin.period(self.PERIOD)
        pwm_pin.prescaler(self.PRESCALER)

        # Set the motor speed to zero if there is a signal sent to kill the program
        atexit.register(self.set_speed, 0)

    def set_speed(self, speed: float) -> None:
        """
        Set the speed of the motor.

        :param speed: desired motor speed
        :type speed: float
        """
        if speed >= 0:
            direction = 1 * self.direction
        elif speed < 0:
            direction = -1 * self.direction

        # If the speed is not set to zero then add the trim
        if 0.001 < abs(speed):
            speed = abs(speed) - self.trim

        if direction < 0:
            self.direction_pin.high()
            self.pwm_pin.pulse_width_percent(speed)
        else:
            self.direction_pin.low()
            self.pwm_pin.pulse_width_percent(speed)
