from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.occasion_update_args_date import OccasionUpdateArgsDate
    from ..models.occasion_update_args_kind import OccasionUpdateArgsKind
    from ..models.occasion_update_args_name import OccasionUpdateArgsName
    from ..models.occasion_update_args_schedulability import OccasionUpdateArgsSchedulability
    from ..models.occasion_update_args_scheduling_event_count import OccasionUpdateArgsSchedulingEventCount
    from ..models.occasion_update_args_scheduling_event_duration_mins import (
        OccasionUpdateArgsSchedulingEventDurationMins,
    )


T = TypeVar("T", bound="OccasionUpdateArgs")


@_attrs_define
class OccasionUpdateArgs:
    """OccasionUpdate args.

    Attributes:
        ref_id (str): A generic entity id.
        name (OccasionUpdateArgsName):
        kind (OccasionUpdateArgsKind):
        date (OccasionUpdateArgsDate):
        schedulability (OccasionUpdateArgsSchedulability):
        scheduling_event_duration_mins (OccasionUpdateArgsSchedulingEventDurationMins):
        scheduling_event_count (OccasionUpdateArgsSchedulingEventCount):
    """

    ref_id: str
    name: OccasionUpdateArgsName
    kind: OccasionUpdateArgsKind
    date: OccasionUpdateArgsDate
    schedulability: OccasionUpdateArgsSchedulability
    scheduling_event_duration_mins: OccasionUpdateArgsSchedulingEventDurationMins
    scheduling_event_count: OccasionUpdateArgsSchedulingEventCount
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        kind = self.kind.to_dict()

        date = self.date.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "kind": kind,
                "date": date,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.occasion_update_args_date import OccasionUpdateArgsDate  # noqa: PLC0415
        from ..models.occasion_update_args_kind import OccasionUpdateArgsKind  # noqa: PLC0415
        from ..models.occasion_update_args_name import OccasionUpdateArgsName  # noqa: PLC0415
        from ..models.occasion_update_args_schedulability import OccasionUpdateArgsSchedulability  # noqa: PLC0415
        from ..models.occasion_update_args_scheduling_event_count import OccasionUpdateArgsSchedulingEventCount  # noqa: PLC0415
        from ..models.occasion_update_args_scheduling_event_duration_mins import (
            OccasionUpdateArgsSchedulingEventDurationMins,  # noqa: PLC0415
        )

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = OccasionUpdateArgsName.from_dict(d.pop("name"))

        kind = OccasionUpdateArgsKind.from_dict(d.pop("kind"))

        date = OccasionUpdateArgsDate.from_dict(d.pop("date"))

        schedulability = OccasionUpdateArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = OccasionUpdateArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = OccasionUpdateArgsSchedulingEventCount.from_dict(d.pop("scheduling_event_count"))

        occasion_update_args = cls(
            ref_id=ref_id,
            name=name,
            kind=kind,
            date=date,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
        )

        occasion_update_args.additional_properties = d
        return occasion_update_args

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
