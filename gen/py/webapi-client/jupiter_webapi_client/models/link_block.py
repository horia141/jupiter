from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.link_block_kind import LinkBlockKind

T = TypeVar("T", bound="LinkBlock")


@_attrs_define
class LinkBlock:
    """A link.

    Attributes:
        correlation_id (str): A generic entity id.
        kind (LinkBlockKind):
        url (str): A URL in this domain.
    """

    correlation_id: str
    kind: LinkBlockKind
    url: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        correlation_id = self.correlation_id

        kind = self.kind.value

        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "kind": kind,
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        correlation_id = d.pop("correlation_id")

        kind = LinkBlockKind(d.pop("kind"))

        url = d.pop("url")

        link_block = cls(
            correlation_id=correlation_id,
            kind=kind,
            url=url,
        )

        link_block.additional_properties = d
        return link_block

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
