class Pin:
    """Mock the Pin class from the robot_hat package."""

    def __init__(self, pin: str) -> None:
        """
        Create a mock Pin instance.

        :param pin: pin to interface with
        :type pin: str
        """
        ...

    def high(self) -> None:
        """Mock the high method which sets a pin value to high."""
        ...

    def low(self) -> None:
        """Mock the low method which sets a pin value to low."""
        ...
