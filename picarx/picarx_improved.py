import atexit
import time
from typing import Any

try:
    from robot_hat import PWM, Grayscale_Module, Pin, Servo, Ultrasonic, fileDB
    from robot_hat.utils import reset_mcu

    reset_mcu()
    time.sleep(0.2)
except (ImportError, ModuleNotFoundError):
    print(
        "This computer does not appear to be a PiCar -X system (robot_hat is not"
        " present). Shadowing hardware calls with substitute functions."
    )
    from sim_robot_hat import PWM, Grayscale_Module, Pin, Servo, Ultrasonic, fileDB


class Picarx:
    """Interface used to control the PiCar-X robot."""

    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02

    def __init__(
        self,
        config: str,
        user: str,
        servo_pins: list[str] = ["P0", "P1", "P2"],
        motor_pins: list[str] = ["D4", "D5", "P12", "P13"],
        grayscale_pins: list[str] = ["A0", "A1", "A2"],
        ultrasonic_pins: list[str] = ["D2", "D3"],
    ):
        """
        Create a new Picarx object.

        :param config: path of config file
        :type config: str, optional
        :param user: owner of the configuration file
        :type user: str
        :param servo_pins: direction_servo, camera_servo_1, camera_servo_2, defaults to
            ["P0", "P1", "P2"]
        :type servo_pins: list[str], optional
        :param motor_pins: left_switch, right_switch, left_pwm, right_pwm, defaults to
            ["D4", "D5", "P12", "P13"]
        :type motor_pins: list[str], optional
        :param grayscale_pins: 3 adc channels, defaults to ["A0", "A1", "A2"]
        :type grayscale_pins: list[str], optional
        :param ultrasonic_pins: tring, echo, defaults to ["D2", "D3"]
        :type ultrasonic_pins: list[str], optional
        """
        # Initialize the configuration file
        self.config_file = fileDB(config, 774, user)

        # Configure interfaces for the car servos
        self.pan_servo = Servo(PWM(servo_pins[0]))
        self.tilt_servo = Servo(PWM(servo_pins[1]))
        self.steering_survo = Servo(PWM(servo_pins[2]))

        # Read the servo trim values
        self.steering_survo_trim = int(
            self.config_file.get("picarx_dir_servo", default_value=0)
        )
        self.pan_servo_trim = int(
            self.config_file.get("picarx_cam_servo1", default_value=0)
        )
        self.tilt_servo_trim = int(
            self.config_file.get("picarx_cam_servo2", default_value=0)
        )

        # Set the trim angles
        self.steering_survo.angle(self.steering_survo_trim)
        self.pan_servo.angle(self.pan_servo_trim)
        self.tilt_servo.angle(self.tilt_servo_trim)

        # Initialize the motors
        self.left_motor_direction_pin = Pin(motor_pins[0])
        self.right_motor_direction_pin = Pin(motor_pins[1])
        self.left_motor_pwm_pin = PWM(motor_pins[2])
        self.right_motor_pwm_pin = PWM(motor_pins[3])

        self.motor_direction_pins = (
            self.left_motor_direction_pin,
            self.right_motor_direction_pin,
        )
        self.motor_speed_pins = (self.left_motor_pwm_pin, self.right_motor_pwm_pin)

        # Get the default motor directions
        self.default_motor_direction = self.config_file.get(
            "picarx_dir_motor", default_value="[1,1]"
        )
        self.default_motor_direction = [
            int(i.strip()) for i in self.default_motor_direction.strip("[]").split(",")
        ]

        self.motor_speed_trims = [0, 0]
        self.turn_angle = 0.0

        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        # Initialize the camera
        self.grayscale = Grayscale_Module(*grayscale_pins, reference=1000)

        # Initialize the ultrasonic sensor
        tring, echo = ultrasonic_pins
        self.ultrasonic = Ultrasonic(Pin(tring), Pin(echo))

        # Register the shutdown method
        atexit.register(self.cleanup)

    def cleanup(self) -> None:
        """Shutdown the car on exit."""
        # Shut the motors off
        self.stop()

    def save_motor_direction_calibration(self, motor: int, value: int) -> None:
        """
        Calibrate the motor direction.

        :param motor: motor to calibrate
        :type motor: int
        :param value: direction of the motor; 1 for positive direction, -1 for negative
            direction
        :type value: int
        """
        motor -= 1

        if value == 1:
            self.default_motor_direction[motor] = 1
        elif value == -1:
            self.default_motor_direction[motor] = -1

        self.config_file.set("picarx_dir_motor", self.default_motor_direction)

    def save_steering_servo_calibration(self, value: int) -> None:
        """
        Calibrate the angle of the direction servo.

        :param value: calibration value
        :type value: int
        """
        self.steering_survo_trim = value
        self.config_file.set("picarx_dir_servo", "%s" % value)
        self.steering_survo.angle(value)

    def save_pan_servo_calibration(self, value: int) -> None:
        """
        Calibrate the camera pan servo.

        :param value: calibration value.
        :type value: int
        """
        self.pan_servo_trim = value
        self.config_file.set("picarx_cam_servo1", "%s" % value)
        self.pan_servo.angle(value)

    def save_tilt_servo_calibration(self, value: int) -> None:
        """
        Calibrate the camera tilt servo.

        :param value: calibration value
        :type value: int
        """
        self.tilt_servo_trim = value
        self.config_file.set("picarx_cam_servo2", "%s" % value)
        self.tilt_servo.angle(value)

    def set_motor_speed(self, motor: int, speed: float) -> None:
        """
        Set the motor speed.

        :param motor: motor whose speed should be set
        :type motor: int
        :param speed: target motor speed
        :type speed: float
        """
        motor -= 1

        if speed >= 0:
            direction = 1 * self.default_motor_direction[motor]
        elif speed < 0:
            direction = -1 * self.default_motor_direction[motor]

        speed = abs(speed) - self.motor_speed_trims[motor]

        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def set_turn_angle(self, value: int) -> None:
        """
        Set the angle of the steering servo.

        :param value: desired angle of the servo
        :type value: int
        """
        self.turn_angle = value
        self.steering_survo.angle(value + self.steering_survo_trim)

    def set_pan_angle(self, value: int) -> None:
        """
        Set the camera pan servo angle.

        :param value: angle
        :type value: int
        """
        self.pan_servo.angle(-1 * (value + -1 * self.pan_servo_trim))

    def set_tilt_angle(self, value: int) -> None:
        """
        Set the camera tilt servo angle.

        :param value: angle
        :type value: int
        """
        self.tilt_servo.angle(-1 * (value + -1 * self.tilt_servo_trim))

    def set_power(self, speed: float) -> None:
        """
        Set the speed for both motors.

        :param speed: desired speed for the motors to drive at.
        :type speed: float
        """
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed)

    def backward(self, speed: float) -> None:
        """
        Drive backward.

        :param speed: desired speed to drive backwards at.
        :type speed: float
        """
        current_angle = self.turn_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)

            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0

            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1 * speed)
                self.set_motor_speed(2, speed * power_scale)
            else:
                self.set_motor_speed(1, -1 * speed * power_scale)
                self.set_motor_speed(2, speed)
        else:
            self.set_motor_speed(1, -1 * speed)
            self.set_motor_speed(2, speed)

    def forward(self, speed: float) -> None:
        """
        Drive forward.

        :param speed: desired speed to drive forward at.
        :type speed: float
        """
        current_angle = self.turn_angle

        if current_angle != 0:
            abs_current_angle = abs(current_angle)

            if abs_current_angle > 40:
                abs_current_angle = 40

            power_scale = (100 - abs_current_angle) / 100.0

            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, 1 * speed * power_scale)
                self.set_motor_speed(2, -speed)
            else:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -1 * speed * power_scale)
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1 * speed)

    def drive(self, speed: float, angle: float) -> None:
        """
        Drive the robot in a desired speed and direction.

        If the speed is positive, then the robot will drive forward, otherwise the
        the robot will attempt to drive backwards.

        :param speed: desired speed
        :type speed: float
        :param angle: desired angle
        :type angle: float
        """
        self.set_turn_angle(angle)

        if speed > 0:
            self.forward(speed)
        else:
            self.backward(-speed)

    def stop(self) -> None:
        """Stop the motors."""
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)

    def get_distance(self) -> float:
        """
        Get the ultrasonic sensor distance.

        :return: distance.
        :rtype: float
        """
        return self.ultrasonic.read()

    def set_grayscale_reference(self, value: Any) -> None:
        """
        Set the greyscale reference.

        :param value: greyscale reference
        :type value: Any
        """
        self.get_grayscale_reference = value

    def get_grayscale_data(self) -> list[Any]:
        """
        Get the greyscale data.

        :return: greyscale data
        :rtype: list[Any]
        """
        return list.copy(self.grayscale.get_grayscale_data())

    def get_line_status(self, gm_val_list: list[Any]) -> str:
        """
        Get the current line status.

        :param gm_val_list: greyscale data
        :type gm_val_list: list[Any]
        :return: line status
        :rtype: str
        """
        return str(self.grayscale.get_line_status(gm_val_list))
