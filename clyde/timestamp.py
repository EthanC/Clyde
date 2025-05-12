"""Define the Timestamp class and its associates."""

from datetime import datetime
from enum import StrEnum


class TimestampStyles(StrEnum):
    """
    Define the available styles of Discord Timestamps.

    https://discord.com/developers/docs/reference#message-formatting-timestamp-styles
    """

    SHORT_TIME = "t"
    """Example Output: 4:20 PM"""

    LONG_TIME = "T"
    """Example Output: 4:20:30 PM"""

    SHORT_DATE = "d"
    """Example Output: 4/20/2025"""

    LONG_DATE = "D"
    """Example Output: April 20, 2025"""

    SHORT_DATE_TIME = "f"
    """Example Output: April 20, 2025 04:20 PM"""

    LONG_DATE_TIME = "F"
    """Example Output: Sunday, April 20, 2025 04:20 PM"""

    RELATIVE_TIME = "R"
    """Example Output: 2 months ago"""


class Timestamp:
    """
    Define static methods for applying Discord Timestamp formatting.

    Timestamps are expressed in seconds and display the given timestamp in the user's
    timezone and locale.

    https://discord.com/developers/docs/reference#message-formatting
    """

    @staticmethod
    def timestamp(value: int | float | str | datetime, style: TimestampStyles) -> str:
        """
        Format the provided timestamp to display in the user's timezone and locale.

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

            style (TimestampStyles): A Timestamp Style.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        if isinstance(value, float):
            value = int(value)
        elif isinstance(value, str):
            value = int(datetime.fromisoformat(value).timestamp())
        elif isinstance(value, datetime):
            value = int(value.timestamp())

        return f"<t:{value}:{style}>"

    @staticmethod
    def short_time(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Short Time.

        Example Output: 4:20 PM

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.SHORT_TIME)

    @staticmethod
    def long_time(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Long Time.

        Example Output: 4:20:30 PM

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.LONG_TIME)

    @staticmethod
    def short_date(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Short Date.

        Example Output: 4/20/2025

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.SHORT_DATE)

    @staticmethod
    def long_date(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Long Date.

        Example Output: April 20, 2025

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.LONG_DATE)

    @staticmethod
    def short_date_time(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Short Date/Time.

        Example Output: April 20, 2025 04:20 PM

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.SHORT_DATE_TIME)

    @staticmethod
    def long_date_time(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Long Date/Time.

        Example Output: Sunday, April 20, 2025 04:20 PM

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.LONG_DATE_TIME)

    @staticmethod
    def relative_time(value: int | float | str | datetime) -> str:
        """
        Format the provided timestamp as Relative Time.

        Example Output: 2 months ago

        Arguments:
            value (int | float | str | datetime): The timestamp expressed in seconds.

        Returns:
            timestamp (str): The formatted timestamp.
        """
        return Timestamp.timestamp(value, TimestampStyles.RELATIVE_TIME)
