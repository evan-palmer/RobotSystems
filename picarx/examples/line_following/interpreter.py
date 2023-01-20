class Interpreter:
    """Interface used to interpret sensor readings."""

    def __init__(self, sensitivity: float = 0.5, polarity: bool = True) -> None:
        """
        Create a new interpreter to evaluate sensor readings.

        :param sensitivity: how different dark and light values are expected to be;
            should be in the range [0, 1], defaults to 0.5
        :type sensitivity: float, optional
        :param polarity: is the line dark (False) or light (True), defaults to True
        :type polarity: bool, optional
        """
        self.sensitivity = max(0, (min(sensitivity, 1))) * (-1 if polarity else 1)

    def detect_direction(self, readings: list[int]) -> float:
        """
        Detect the direction of the line.

        :param readings: photosensor readings
        :type readings: list[int]
        :return: measured direction of the line (if one exists)
        :rtype: float
        """
        left, middle, right = readings
        return (right - left) / middle * self.sensitivity
