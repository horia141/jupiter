from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="HomeWidgetMoveAndResizeArgs")


@_attrs_define
class HomeWidgetMoveAndResizeArgs:
    """The arguments for moving a home widget.

    Attributes:
        ref_id (str): A generic entity id.
        row (int):
        col (int):
    """

    ref_id: str
    row: int
    col: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        row = self.row

        col = self.col

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "row": row,
                "col": col,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        row = d.pop("row")

        col = d.pop("col")

        home_widget_move_and_resize_args = cls(
            ref_id=ref_id,
            row=row,
            col=col,
        )

        home_widget_move_and_resize_args.additional_properties = d
        return home_widget_move_and_resize_args

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
