from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.quote_block_kind import QuoteBlockKind

T = TypeVar("T", bound="QuoteBlock")


@_attrs_define
class QuoteBlock:
    """A quote.

    Attributes:
        correlation_id (str): A generic entity id.
        kind (QuoteBlockKind):
        text (str):
    """

    correlation_id: str
    kind: QuoteBlockKind
    text: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        correlation_id = self.correlation_id

        kind = self.kind.value

        text = self.text

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "kind": kind,
                "text": text,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        correlation_id = d.pop("correlation_id")

        kind = QuoteBlockKind(d.pop("kind"))

        text = d.pop("text")

        quote_block = cls(
            correlation_id=correlation_id,
            kind=kind,
            text=text,
        )

        quote_block.additional_properties = d
        return quote_block

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
