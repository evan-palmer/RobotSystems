from typing import Any


class fileDB:
    """Mock the fileDB class from the robot_hat package."""

    def __init__(
        self, db: str, mode: str | None = None, owner: str | None = None
    ) -> None:
        """
        Create a new instance of the mock fileDB class.

        :param db: database name
        :type db: str
        :param mode: file special mode flags (used by chmod), defaults to None
        :type mode: str | None, optional
        :param owner: file owner (used by chown), defaults to None
        :type owner: str | None, optional
        """
        ...

    def file_check_create(
        self, file_path: str, mode: str | None = None, owner: str | None = None
    ) -> None:
        """
        Create a new file for the DB.

        :param file_path: full path to the file
        :type file_path: str
        :param mode: file special mode flags, defaults to None
        :type mode: str | None, optional
        :param owner: file owner, defaults to None
        :type owner: str | None, optional
        """
        ...

    def get(self, name: str, default_value: Any | None = None) -> Any:
        """
        Mock the get method; attempts to read a property from the file.

        :param name: property name
        :type name: str
        :param default_value: default value to return if the property doesn't exist.
        :type default_value: Any
        :return: None
        :rtype: Any
        """
        return None

    def set(self, name: str, value: Any) -> None:
        """
        Mock the set method; attempts to write the value of a property.

        :param name: property name
        :type name: str
        :param value: value to set the property to
        :type value: Any
        """
        ...
