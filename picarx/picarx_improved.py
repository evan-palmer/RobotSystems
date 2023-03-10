import time
from typing import Any, Union

import numpy as np

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

from motor import Motor


class Picarx:
    """Interface used to control the PiCar-X robot."""

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

        # Get the default motor configurations
        self.default_motor_direction = self.config_file.get(
            "picarx_dir_motor", default_value="[1,1]"
        )
        self.default_motor_speed = self.config_file.get(
            "picarx_motor_trim", default_value="[25,0]"
        )
        self.default_motor_direction = [
            int(i.strip()) for i in self.default_motor_direction.strip("[]").split(",")
        ]
        self.default_motor_speed = [
            int(i.strip()) for i in self.default_motor_speed.strip("[]").split(",")
        ]

        # Initialize the motors
        self.right_motor = Motor(
            Pin(motor_pins[0]),
            PWM(motor_pins[2]),
            default_direction=self.default_motor_direction[0],
            trim=self.default_motor_speed[0],
        )
        self.left_motor = Motor(
            Pin(motor_pins[1]),
            PWM(motor_pins[3]),
            default_direction=self.default_motor_direction[1],
            trim=self.default_motor_speed[1],
        )

        self.turn_angle = 0.0

        # Initialize the camera
        self.grayscale = Grayscale_Module(*grayscale_pins, reference=1000)

        # Initialize the ultrasonic sensor
        tring, echo = ultrasonic_pins
        self.ultrasonic = Ultrasonic(Pin(tring), Pin(echo))

    def reset(self) -> None:
        """Reset the state of the car."""
        # Stop the motors
        self.stop()

        # Reset the servos
        self.set_pan_angle(0)
        self.set_turn_angle(0)
        self.set_tilt_angle(0)

    def save_motor_direction_calibration(self, motor: int, value: int) -> None:
        """
        Save the calibrated motor direction.

        :param motor: motor whose calibration should be saved
        :type motor: int
        :param value: direction of the motor; 1 for positive direction, -1 for negative
            direction
        :type value: int
        """
        if motor not in [1, 2]:
            raise ValueError("Invalid motor ID provided. Options are: 1, 2.")

        if motor == 1:
            self.right_motor.direction = value
        else:
            self.left_motor.direction = value

        self.config_file.set(
            "picarx_dir_motor", [self.right_motor.direction, self.left_motor.direction]
        )

    def save_motor_speed_calibration(self, motor: int, value: int) -> None:
        """
        Save the calibrated motor speed (trim).

        :param motor: motor whose calibration should be saved
        :type motor: int
        :param value: motor speed trim
        :type value: int
        """
        if motor not in [1, 2]:
            raise ValueError("Invalid motor ID provided. Options are: 1, 2.")

        if motor == 1:
            self.right_motor.trim = value
        else:
            self.left_motor.trim = value

        self.config_file.set(
            "picarx_motor_trim", [self.right_motor.trim, self.left_motor.trim]
        )

    def save_steering_servo_calibration(self, value: int) -> None:
        """
        Save the steering servo calibration.

        :param value: calibration value
        :type value: int
        """
        self.steering_survo_trim = value
        self.config_file.set("picarx_dir_servo", "%s" % value)
        self.steering_survo.angle(value)

    def save_pan_servo_calibration(self, value: int) -> None:
        """
        Save the camera panning servo calibration.

        :param value: calibration value
        :type value: int
        """
        self.pan_servo_trim = value
        self.config_file.set("picarx_cam_servo1", "%s" % value)
        self.pan_servo.angle(value)

    def save_tilt_servo_calibration(self, value: int) -> None:
        """
        Svae the camera tilt servo calibration.

        :param value: calibration value
        :type value: int
        """
        self.tilt_servo_trim = value
        self.config_file.set("picarx_cam_servo2", "%s" % value)
        self.tilt_servo.angle(value)

    def set_turn_angle(self, value: float) -> None:
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
        self.right_motor.set_speed(speed)
        self.left_motor.set_speed(speed)

    def calculate_speed(self, angle: float) -> float:
        """
        Calculate the wheel speed given the desired steering angle.

        :param angle: desired steering angle
        :type angle: float
        :return: target wheel speed
        :rtype: float
        """
        length = 11.8
        height = 9.5

        icr = np.tan(90 - abs(angle)) * height + length / 2
        scale = (icr - length / 2) / icr

        return abs(scale)

    def drive(self, speed: float, angle: Union[float, None] = None) -> None:
        """
        Drive the robot in a desired speed and direction.

        If the speed is positive, then the robot will drive forward, otherwise the
        the robot will attempt to drive backwards.
        :param speed: desired speed
        :type speed: float
        :param angle: desired angle
        :type angle: float
        """
        if angle is None:
            angle = self.turn_angle
        else:
            self.set_turn_angle(angle)

        if angle != 0:
            abs_angle = abs(angle)

            if abs_angle > 40:
                abs_angle = 40

            power_scale = self.calculate_speed(abs_angle)

            if speed > 0:
                if (angle / abs_angle) > 0:
                    self.right_motor.set_speed(speed * power_scale)
                    self.left_motor.set_speed(-speed)
                else:
                    self.right_motor.set_speed(speed)
                    self.left_motor.set_speed(-speed * power_scale)
            else:
                if (angle / abs_angle) > 0:
                    self.right_motor.set_speed(speed)
                    self.left_motor.set_speed(-speed * power_scale)
                else:
                    self.right_motor.set_speed(speed * power_scale)
                    self.left_motor.set_speed(-speed)
        else:
            self.right_motor.set_speed(speed)
            self.left_motor.set_speed(-speed)

    def stop(self) -> None:
        """Stop the motors."""
        self.set_power(0)

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
