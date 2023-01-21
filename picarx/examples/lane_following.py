import math
import sys
from typing import Any

import cv2
import numpy as np

sys.path.append("..")

from picarx_improved import Picarx  # noqa


class LaneDetector:
    """Interface used to detect lanes on a Picarx."""

    WIDTH = 320
    HEIGHT = 240

    def __init__(self) -> None:
        pass

    def _detect_edges(self, frame: cv2.Mat) -> Any:
        """_summary_

        :param frame: _description_
        :type frame: cv2.Mat
        :return: _description_
        :rtype: Any
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([60, 40, 40])
        upper_blue = np.array([150, 255, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        edges = cv2.Canny(mask, 200, 400)

        return edges

    def detect_line_segments(self, cropped_edges: cv2.Mat) -> Any:
        """_summary_

        :param cropped_edges: _description_
        :type cropped_edges: cv2.Mat
        :return: _description_
        :rtype: Any
        """
        rho = 1
        angle = np.pi / 180
        min_threshold = 10
        line_segments = cv2.HoughLinesP(
            cropped_edges,
            rho,
            angle,
            min_threshold,
            np.array([]),
            minLineLength=8,
            maxLineGap=4,
        )

        return line_segments

    def average_slope_intercept(
        self, frame: cv2.Mat, line_segments: list[cv2.Mat] | None
    ) -> list[list[list[int]]]:
        """
        pain.

        :param frame: _description_
        :type frame: cv2.Mat
        :param line_segments: _description_
        :type line_segments: list[cv2.Mat] | None
        :return: _description_
        :rtype: list[list[list[int]]]
        """
        lane_lines: list[list[list[int]]] = []

        if line_segments is None:
            return lane_lines

        _, width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1 / 3
        left_region_boundary = width * (1 - boundary)
        right_region_boundary = width * boundary

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    continue

                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]

                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)

        if len(left_fit) > 0:
            lane_lines.append(self.make_points(frame, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)

        if len(right_fit) > 0:
            lane_lines.append(self.make_points(frame, right_fit_average))

        return lane_lines

    def make_points(self, frame: cv2.Mat, line: np.ndarray) -> list[list[int]]:
        """
        pain.

        :param frame: _description_
        :type frame: cv2.Mat
        :param line: _description_
        :type line: np.ndarray
        :return: _description_
        :rtype: list[list[int]]
        """
        height, width, _ = frame.shape
        slope, intercept = line
        y1 = height
        y2 = int(y1 * 1 / 2)

        x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))

        return [[x1, y1, x2, y2]]

    def region_of_interest(canny):
        height, width = canny.shape
        mask = np.zeros_like(canny)

        # only focus bottom half of the screen

        polygon = np.array(
            [
                [
                    (0, height * 1 / 2),
                    (width, height * 1 / 2),
                    (width, height),
                    (0, height),
                ]
            ],
            np.int32,
        )

        cv2.fillPoly(mask, polygon, 255)
        masked_image = cv2.bitwise_and(canny, mask)
        return masked_image

    def compute_steering_angle(frame, lane_lines):
        if len(lane_lines) == 0:
            return -90

        height, width, _ = frame.shape
        if len(lane_lines) == 1:
            x1, _, x2, _ = lane_lines[0][0]
            x_offset = x2 - x1
        else:
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            camera_mid_offset_percent = 0.02
            mid = int(width / 2 * (1 + camera_mid_offset_percent))
            x_offset = (left_x2 + right_x2) / 2 - mid

        y_offset = int(height / 2)

        angle_to_mid_radian = math.atan(
            x_offset / y_offset
        )  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
        steering_angle = angle_to_mid_deg + 90
        return steering_angle

    def stabilize_steering_angle(
        self,
        curr_steering_angle,
        new_steering_angle,
        num_of_lane_lines,
        max_angle_deviation_two_lines=5,
        max_angle_deviation_one_lane=1,
    ):
        if num_of_lane_lines == 2:
            # if both lane lines detected, then we can deviate more
            max_angle_deviation = max_angle_deviation_two_lines
        else:
            max_angle_deviation = max_angle_deviation_one_lane

        angle_deviation = new_steering_angle - curr_steering_angle

        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(
                curr_steering_angle
                + max_angle_deviation * angle_deviation / abs(angle_deviation)
            )
        else:
            stabilized_steering_angle = new_steering_angle

        return stabilized_steering_angle


def lane_following(config: str, user: str) -> None:
    ...
