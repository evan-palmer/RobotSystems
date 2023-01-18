class PWM:
    """Mock the PWM class from the robot_hat package."""

    def __init__(self, channel: str, debug: str = "critical") -> None:
        """
        Create a new mock PWM instance.

        :param channel: servo pin
        :type channel: str
        :param debug: log level, defaults to "critical"
        :type debug: str, optional
        """
        ...
