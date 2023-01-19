from typing import Any


class ADC:
    """Mock interface for an ADC."""

    def __init__(self, channel: str) -> None:
        """
        Create a new mock ADC interface.

        :param channel: ADC channel
        :type channel: str
        """
        ...

    def read(self) -> Any:
        """
        Mock the read method; returns a reading from the specified ADC.

        :return: mock ADC reading: 0
        :rtype: Any
        """
        return 0.0

    def read_voltage(self) -> float:
        """
        Mock the read_voltage method; read the ADC pin voltage level.

        :return: mock voltage: 0
        :rtype: float
        """
        return 0.0
