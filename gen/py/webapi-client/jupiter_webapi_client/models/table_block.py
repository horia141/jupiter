from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.table_block_kind import TableBlockKind

T = TypeVar("T", bound="TableBlock")


@_attrs_define
class TableBlock:
    """A table.

    Attributes:
        correlation_id (str): A generic entity id.
        kind (TableBlockKind):
        with_header (bool):
        contents (List[List[str]]):
    """

    correlation_id: str
    kind: TableBlockKind
    with_header: bool
    contents: List[List[str]]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        correlation_id = self.correlation_id

        kind = self.kind.value

        with_header = self.with_header

        contents = []
        for contents_item_data in self.contents:
            contents_item = contents_item_data

            contents.append(contents_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "kind": kind,
                "with_header": with_header,
                "contents": contents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        correlation_id = d.pop("correlation_id")

        kind = TableBlockKind(d.pop("kind"))

        with_header = d.pop("with_header")

        contents = []
        _contents = d.pop("contents")
        for contents_item_data in _contents:
            contents_item = cast(List[str], contents_item_data)

            contents.append(contents_item)

        table_block = cls(
            correlation_id=correlation_id,
            kind=kind,
            with_header=with_header,
            contents=contents,
        )

        table_block.additional_properties = d
        return table_block

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
