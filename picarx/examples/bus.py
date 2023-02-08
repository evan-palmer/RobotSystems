import threading
from typing import Any


class Bus:
    """Interface used for message passing between threads."""

    def __init__(self) -> None:
        """Create a new bus."""
        self.message = None
        self._lock = threading.Lock()

    def read(self) -> Any:
        """
        Get the bus message.

        :return: current message stored in the bus
        :rtype: Any
        """
        with self._lock:
            return self.message

    def write(self, msg: Any) -> None:
        """
        Write a new message to the bus.

        :param msg: message to write
        :type msg: Any
        """
        with self._lock:
            self.message = msg
