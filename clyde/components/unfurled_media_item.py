"""Define the Unfurled Media Item class and its associates."""

from typing import Self

import msgspec
from msgspec import UNSET, Struct, UnsetType


class UnfurledMediaItem(Struct, kw_only=True):
    """
    Represent an Unfurled Media Item structure.

    https://discord.com/developers/docs/components/reference#unfurled-media-item-structure

    Attributes:
        url (str): Supports arbitrary URLs and attachment://<filename> references.
    """

    url: UnsetType | str = msgspec.field(default=UNSET)
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
