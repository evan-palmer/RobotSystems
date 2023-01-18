from typing import Any


class Grayscale_Module:
    """Simulated Grayscale_Module class from the robot_hat package."""

    def __init__(self, pin0: str, pin1: str, pin2: str, reference: int = 1000) -> None:
        """
        Create a new mock Grayscale_Module instance.

        :param pin0: grayscale ADC channel 0
        :type pin0: str
        :param pin1: grayscale ADC channel 1
        :type pin1: str
        :param pin2: grayscale ADC channel 2
        :type pin2: str
        :param reference: grayscale reference value, defaults to 1000
        :type reference: int, optional
        """
        ...

    def get_grayscale_data(self) -> list[Any]:
        """
        Mock the get_grayscale_data method.

        :return: empty list
        :rtype: list[Any]
        """
        return []

    def get_line_status(self, fl_list: list[int]) -> str:
        """
        Mock the get_line_status method.

        :param fl_list: greyscale data
        :type fl_list: list[int]
        :return: fun string
        :rtype: str
        """
        return "party time"
