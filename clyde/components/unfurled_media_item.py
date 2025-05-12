"""Define the Unfurled Media Item class and its associates."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from clyde.validation import Validation


class UnfurledMediaItem(BaseModel):
    """
    Represent an Unfurled Media Item structure.

    https://discord.com/developers/docs/components/reference#unfurled-media-item-structure

    Attributes:
        url (str): Supports arbitrary URLs and attachment://<filename> references.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Unfurled Media Item class."""

    url: str | None = Field(default=None)
    """Supports arbitrary URLs and attachment://<filename> references."""

    def set_url(self: Self, url: str) -> "UnfurledMediaItem":
        """
        Set the URL of the Unfurled Media Item.

        Arguments:
            url (str): Supports arbitrary URLs and attachment://<filename> references.

        Returns:
            self (UnfurledMediaItem): The modified Unfurled Media Item instance.
        """
        self.url = url

        return self

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        """
        Validate the value of URL for an Unfurled Media Item.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(url, ["http", "https", "attachment"])
