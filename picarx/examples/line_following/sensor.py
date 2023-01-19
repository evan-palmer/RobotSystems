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

    def __init__(self, pin_1: str, pin_2: str, pin_3: str) -> None:
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

    def read(self) -> list[int]:
        """
        Read the ADC values from the ground-facing photosensor.

        :return: readings from the three ADC channels
        :rtype: list[int]
        """
        return [self.channel_1.read(), self.channel_2.read(), self.channel_3.read()]
