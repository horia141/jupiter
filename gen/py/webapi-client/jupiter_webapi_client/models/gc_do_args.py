from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="GCDoArgs")


@_attrs_define
class GCDoArgs:
    """GCArgs.

    Attributes:
        source (EventSource): The source of the modification which this event records.
        gc_targets (Union[Unset, List[SyncTarget]]):
    """

    source: EventSource
    gc_targets: Union[Unset, List[SyncTarget]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source = self.source.value

        gc_targets: Union[Unset, List[str]] = UNSET
        if not isinstance(self.gc_targets, Unset):
            gc_targets = []
            for gc_targets_item_data in self.gc_targets:
                gc_targets_item = gc_targets_item_data.value
                gc_targets.append(gc_targets_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
            }
        )
        if gc_targets is not UNSET:
            field_dict["gc_targets"] = gc_targets

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        source = EventSource(d.pop("source"))

        gc_targets = []
        _gc_targets = d.pop("gc_targets", UNSET)
        for gc_targets_item_data in _gc_targets or []:
            gc_targets_item = SyncTarget(gc_targets_item_data)

            gc_targets.append(gc_targets_item)

        gc_do_args = cls(
            source=source,
            gc_targets=gc_targets,
        )

        gc_do_args.additional_properties = d
        return gc_do_args

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
