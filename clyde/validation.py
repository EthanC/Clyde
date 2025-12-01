"""Define the Validation class and its associates."""

from datetime import datetime

from msgspec import Meta, Struct, inspect
from msgspec.inspect import Field, StrType, StructType, Type, type_info


class Validation:
    """Define static methods for reusable data validation and conversion."""

    @staticmethod
    def convert_color(value: str | int) -> int:
        """
        Convert, if applicable, a color value for Discord.

        Arguments:
            value (str | int): The value to validate.

        Returns:
            value (int): The validated color value.
        """
        if isinstance(value, str):
            if value.startswith("#"):
                # Discard the # in a hex color code
                value = value[1:]

            value = int(value, base=16)

        return value

    @staticmethod
    def convert_timestamp(value: int | float | str | datetime) -> str:
        """
        Convert, if applicable, a timestamp value for Discord.

        Arguments:
            value (int | float | str | datetime): The value to validate.

        Returns:
            value (str): The validated value.
        """
        if isinstance(value, int):
            value = datetime.fromtimestamp(float(value))
        elif isinstance(value, float):
            value = datetime.fromtimestamp(value)
        elif isinstance(value, str):
            value = datetime.fromisoformat(value)

        return value.isoformat()

    @staticmethod
    def validate_url_scheme(value: str | None, valid_scheme: list[str]) -> str:
        """
        Validate a URL value contains a valid scheme.

        Arguments:
            value (str): The URL to validate.

            valid_scheme (list[str]): A list of valid URL schemes.

        Returns:
            value (str): The validated URL.
        """
        if not value:
            raise ValueError(
                f"Empty URL is not valid for scheme(s) {', '.join(valid_scheme)}"
            )

        return value

    @staticmethod
    def get_max_length(struct: object, field_name: str) -> int | None:
        """
        Return the maximum string length of a Struct Field.

        Arguments:
            struct (Struct): A msgspec Struct.

            field_name (str): Name of the Field to inspect.

        Returns:
            value (int | None): Maximum string length of the Field, if available.
        """
        struct_info: Type = type_info(struct)

        if not isinstance(struct_info, StructType):
            return

        for field in struct_info.fields:
            if field.name != field_name:
                continue

            field_info: Type = field.type

            if not isinstance(field_info, StrType):
                continue

            return getattr(field_info, "max_length")
