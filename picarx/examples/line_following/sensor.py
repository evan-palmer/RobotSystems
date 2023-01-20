try:
    from robot_hat import ADC
except (ImportError, ModuleNotFoundError):
    print(
        "This computer does not appear to be a PiCar -X system (robot_hat is not"
        " present). Shadowing hardware calls with substitute functions."
    )
    import sys

    sys.path.append("../..")

    from sim_robot_hat import ADC


class Sensor:
    """Interface used to read data from the on-board ground-scanning photosensors."""

    def __init__(self, pin_1: str = "A0", pin_2: str = "A1", pin_3: str = "A2") -> None:
        """
        Create a new interface for reading from the photosensor.

        :param pin_1: ADC channel 1 pin
        :type pin_1: str
        :param pin_2: ADC channel 2 pin
        :type pin_2: str
        :param pin_3: ADC channel 3 pin
        :type pin_3: str
        """
        self.channel_1 = ADC(pin_1)
        self.channel_2 = ADC(pin_2)
        self.channel_3 = ADC(pin_3)

        self.channel_1_trim = 0
        self.channel_2_trim = 0
        self.channel_3_trim = 0

    def read(self) -> list[int]:
        """
        Read the ADC values from the ground-facing photosensor.

        :return: readings from the three ADC channels
        :rtype: list[int]
        """
        return [
            max(a - b, 0)
            for a, b in zip(
                [self.channel_1.read(), self.channel_2.read(), self.channel_3.read()],
                [self.channel_1_trim, self.channel_2_trim, self.channel_3_trim],
            )
        ]

    def calibrate(self, calibration_t: float = 2.0) -> None:
        """Configure the default values for each of the channels."""
        (self.channel_1_trim, self.channel_2_trim, self.channel_3_trim) = self.read()
