import cv2
import time
import Camera
import math
import threading
from LABConfig import color_range
import ArmIK.Transform as transform
from ArmIK.ArmMoveIK import ArmIK
import HiwonderSDK.Board as Board
import CameraCalibration.CalibrationConfig as configs


class ColorSorter:
    SERVO_1_ANGLE = 500  # angle at which the clamper is closed when gripping

    def __init__(self) -> None:
        self.rgb_ranges = {
            "red": (0, 0, 255),
            "blue": (255, 0, 0),
            "green": (0, 255, 0),
            "black": (0, 0, 0),
            "white": (255, 255, 255),
        }
        self.target_color = "red"
        self.arm_ik_interface = ArmIK()
        self.count = 0
        self.stop = False
        self.color_list: list[int] = []
        self.get_roi = False
        self.is_running = False
        self.detect_color = "None"
        self.start_pick_up = False
        self.start_count_t1 = True

    def reset(self) -> None:
        """Reset the script state."""
        self.count = 0
        self.stop_running = False
        self.color_list = []
        self.get_roi = False
        self.target_color = ()
        self.detect_color = "None"
        self.start_pick_up = False
        self.start_count_t1 = True

    def find_area_max_contour(self, contours: list) -> tuple:
        """
        Find the maximum area contour.

        :param contours: contours to search
        :type contours: list
        :return: contour with the max area
        :rtype: tuple
        """
        contour_area_temp = 0.0
        contour_area_max = 0.0
        area_max_contour = None

        for c in contours:
            # calculate the countour area
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp

                # only when the area is greater than 300, the contour of the maximum
                # area is effective to filter interference
                if contour_area_temp > 300:
                    area_max_contour = c

        # return the maximum area countour
        return area_max_contour, contour_area_max

    def init(self) -> None:
        """Move to the initial position."""
        Board.setBusServoPulse(1, self.SERVO_1_ANGLE - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.arm_ik_interface.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def start(self) -> None:
        """Start the color sorter."""
        self.reset()
        self.is_running = True

    def stop(self) -> None:
        """Stop the color sorter."""
        self.stop_running = True
        self.is_running = False

    @staticmethod
    def buzz(duration: float) -> None:
        """
        Run the board buzzer.

        :param duration: duration to run the buzzer for
        :type duration: float
        """
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(duration)
        Board.setBuzzer(0)

    @staticmethod
    def set_board_rgb(color: str) -> None:
        """
        Set the RGB light color of the expansion board to match the color to be tracked.

        :param color: color to set the light to
        :type color: str
        """
        match color:
            case "red":
                Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
                Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
                Board.RGB.show()
            case "green":
                Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
                Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
                Board.RGB.show()
            case "blue":
                Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
                Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
                Board.RGB.show()
            case _:
                Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
                Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
                Board.RGB.show()
