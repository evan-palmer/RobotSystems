class Ultrasonic:
    """Mock the Ultrasonic class from the robot_hat package."""

    def __init__(self, tring: str, echo: str, timeout: float = 0.02) -> None:
        """
        Create a new mock Ultrasonic class.

        :param tring: ultrasonic sensor tring pin
        :type tring: str
        :param echo: ultrasonic sensor echo pin
        :type echo: str
        :param timeout: maximum time before a read attempt times out, defaults to 0.02
        :type timeout: float, optional
        """
        ...

    def read(self) -> float:
        """
        Mock the read method which gets a sensor reading from the ultrasonic sensor.

        :return: dummy float; 0.0
        :rtype: float
        """
        return 0.0
