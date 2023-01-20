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
        self.sensitivity = self.clamp(sensitivity, 0, 1) * (1 if polarity else -1)

    def clamp(self, value: int, min_value: int, max_value: int) -> int:
        return max(min_value, (min(value, max_value)))

    def detect_direction(self, readings: list[int], noise_thresh: int = 10) -> float:
        """
        Detect the direction of the line.

        :param readings: photosensor readings
        :type readings: list[int]
        :return: measured direction of the line (if one exists)
        :rtype: float
        """
        # Add a bit of noise to prevent division by zero errors
        readings = [x + 1 if x == 0 else x for x in readings]
        left, middle, right = readings

        # Break early
        if abs((left - middle) - (right - middle)) < noise_thresh:
            return 0

        # Calculate the direction to turn
        if right - left > 0:
            direction = (middle - right) / (middle + right)
            direction *= -1
        else:
            direction = (middle - left) / (middle + left)

        return direction * self.sensitivity