from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.working_mem_update_settings_args_generation_period import WorkingMemUpdateSettingsArgsGenerationPeriod
    from ..models.working_mem_update_settings_args_schedulability import WorkingMemUpdateSettingsArgsSchedulability
    from ..models.working_mem_update_settings_args_scheduling_event_count import (
        WorkingMemUpdateSettingsArgsSchedulingEventCount,
    )
    from ..models.working_mem_update_settings_args_scheduling_event_duration_mins import (
        WorkingMemUpdateSettingsArgsSchedulingEventDurationMins,
    )


T = TypeVar("T", bound="WorkingMemUpdateSettingsArgs")


@_attrs_define
class WorkingMemUpdateSettingsArgs:
    """PersonFindArgs.

    Attributes:
        generation_period (WorkingMemUpdateSettingsArgsGenerationPeriod):
        schedulability (WorkingMemUpdateSettingsArgsSchedulability):
        scheduling_event_duration_mins (WorkingMemUpdateSettingsArgsSchedulingEventDurationMins):
        scheduling_event_count (WorkingMemUpdateSettingsArgsSchedulingEventCount):
    """

    generation_period: WorkingMemUpdateSettingsArgsGenerationPeriod
    schedulability: WorkingMemUpdateSettingsArgsSchedulability
    scheduling_event_duration_mins: WorkingMemUpdateSettingsArgsSchedulingEventDurationMins
    scheduling_event_count: WorkingMemUpdateSettingsArgsSchedulingEventCount
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation_period = self.generation_period.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_period": generation_period,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.working_mem_update_settings_args_generation_period import (
            WorkingMemUpdateSettingsArgsGenerationPeriod,  # noqa: PLC0415
        )
        from ..models.working_mem_update_settings_args_schedulability import WorkingMemUpdateSettingsArgsSchedulability  # noqa: PLC0415
        from ..models.working_mem_update_settings_args_scheduling_event_count import (
            WorkingMemUpdateSettingsArgsSchedulingEventCount,  # noqa: PLC0415
        )
        from ..models.working_mem_update_settings_args_scheduling_event_duration_mins import (
            WorkingMemUpdateSettingsArgsSchedulingEventDurationMins,  # noqa: PLC0415
        )

        d = dict(src_dict)
        generation_period = WorkingMemUpdateSettingsArgsGenerationPeriod.from_dict(d.pop("generation_period"))

        schedulability = WorkingMemUpdateSettingsArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = WorkingMemUpdateSettingsArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = WorkingMemUpdateSettingsArgsSchedulingEventCount.from_dict(
            d.pop("scheduling_event_count")
        )

        working_mem_update_settings_args = cls(
            generation_period=generation_period,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
        )

        working_mem_update_settings_args.additional_properties = d
        return working_mem_update_settings_args

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
