from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="GCDoArgs")


@_attrs_define
class GCDoArgs:
    """GCArgs.

    Attributes:
        gc_targets (Union[None, Unset, list[SyncTarget]]):
    """

    gc_targets: Union[None, Unset, list[SyncTarget]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        gc_targets: Union[None, Unset, list[str]]
        if isinstance(self.gc_targets, Unset):
            gc_targets = UNSET
        elif isinstance(self.gc_targets, list):
            gc_targets = []
            for gc_targets_type_0_item_data in self.gc_targets:
                gc_targets_type_0_item = gc_targets_type_0_item_data.value
                gc_targets.append(gc_targets_type_0_item)

        else:
            gc_targets = self.gc_targets

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if gc_targets is not UNSET:
            field_dict["gc_targets"] = gc_targets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_gc_targets(data: object) -> Union[None, Unset, list[SyncTarget]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                gc_targets_type_0 = []
                _gc_targets_type_0 = data
                for gc_targets_type_0_item_data in _gc_targets_type_0:
                    gc_targets_type_0_item = SyncTarget(gc_targets_type_0_item_data)

                    gc_targets_type_0.append(gc_targets_type_0_item)

                return gc_targets_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[SyncTarget]], data)

        gc_targets = _parse_gc_targets(d.pop("gc_targets", UNSET))

        gc_do_args = cls(
            gc_targets=gc_targets,
        )

        gc_do_args.additional_properties = d
        return gc_do_args

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
