from sim_robot_hat.pwm import PWM


class Servo:
    """Mock the Servo class from the robot_hat package."""

    def __init__(self, pwm: PWM) -> None:
        """
        Create new mock instance of the PWM class.

        :param pwm: PWM interface for a port
        :type pwm: PWM
        """
        ...

    def angle(self, angle: float) -> None:
        """
        Mock the angle method which attempts to set a desired servo angle.

        :param angle: desired angle
        :type angle: float
        """
        ...

    def set_pwm(self, pwm_value: int) -> None:
        """
        Mock the set_pwm method which sets the PWM value for a port.

        :param pwm_value: desired PWM value
        :type pwm_value: int
        """
        ...
