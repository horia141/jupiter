from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MOTD")


@_attrs_define
class MOTD:
    """A Message of the Day.

    Attributes:
        quote (str):
        author (str):
        wikiquote_link (str): A URL in this domain.
    """

    quote: str
    author: str
    wikiquote_link: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        quote = self.quote

        author = self.author

        wikiquote_link = self.wikiquote_link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "quote": quote,
                "author": author,
                "wikiquote_link": wikiquote_link,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        quote = d.pop("quote")

        author = d.pop("author")

        wikiquote_link = d.pop("wikiquote_link")

        motd = cls(
            quote=quote,
            author=author,
            wikiquote_link=wikiquote_link,
        )

        motd.additional_properties = d
        return motd

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
