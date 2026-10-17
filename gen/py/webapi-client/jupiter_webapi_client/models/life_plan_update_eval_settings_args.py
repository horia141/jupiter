from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.life_plan_update_eval_settings_args_eval_approach import LifePlanUpdateEvalSettingsArgsEvalApproach
    from ..models.life_plan_update_eval_settings_args_eval_periods import LifePlanUpdateEvalSettingsArgsEvalPeriods
    from ..models.life_plan_update_eval_settings_args_eval_task_difficulty import (
        LifePlanUpdateEvalSettingsArgsEvalTaskDifficulty,
    )
    from ..models.life_plan_update_eval_settings_args_eval_task_eisen import LifePlanUpdateEvalSettingsArgsEvalTaskEisen
    from ..models.life_plan_update_eval_settings_args_eval_task_generation_in_advance_days import (
        LifePlanUpdateEvalSettingsArgsEvalTaskGenerationInAdvanceDays,
    )
    from ..models.life_plan_update_eval_settings_args_schedulability import LifePlanUpdateEvalSettingsArgsSchedulability
    from ..models.life_plan_update_eval_settings_args_scheduling_event_count import (
        LifePlanUpdateEvalSettingsArgsSchedulingEventCount,
    )
    from ..models.life_plan_update_eval_settings_args_scheduling_event_duration_mins import (
        LifePlanUpdateEvalSettingsArgsSchedulingEventDurationMins,
    )


T = TypeVar("T", bound="LifePlanUpdateEvalSettingsArgs")


@_attrs_define
class LifePlanUpdateEvalSettingsArgs:
    """Args.

    Attributes:
        eval_periods (LifePlanUpdateEvalSettingsArgsEvalPeriods):
        eval_approach (LifePlanUpdateEvalSettingsArgsEvalApproach):
        eval_task_eisen (LifePlanUpdateEvalSettingsArgsEvalTaskEisen):
        eval_task_difficulty (LifePlanUpdateEvalSettingsArgsEvalTaskDifficulty):
        eval_task_generation_in_advance_days (LifePlanUpdateEvalSettingsArgsEvalTaskGenerationInAdvanceDays):
        schedulability (LifePlanUpdateEvalSettingsArgsSchedulability):
        scheduling_event_duration_mins (LifePlanUpdateEvalSettingsArgsSchedulingEventDurationMins):
        scheduling_event_count (LifePlanUpdateEvalSettingsArgsSchedulingEventCount):
    """

    eval_periods: LifePlanUpdateEvalSettingsArgsEvalPeriods
    eval_approach: LifePlanUpdateEvalSettingsArgsEvalApproach
    eval_task_eisen: LifePlanUpdateEvalSettingsArgsEvalTaskEisen
    eval_task_difficulty: LifePlanUpdateEvalSettingsArgsEvalTaskDifficulty
    eval_task_generation_in_advance_days: LifePlanUpdateEvalSettingsArgsEvalTaskGenerationInAdvanceDays
    schedulability: LifePlanUpdateEvalSettingsArgsSchedulability
    scheduling_event_duration_mins: LifePlanUpdateEvalSettingsArgsSchedulingEventDurationMins
    scheduling_event_count: LifePlanUpdateEvalSettingsArgsSchedulingEventCount
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        eval_periods = self.eval_periods.to_dict()

        eval_approach = self.eval_approach.to_dict()

        eval_task_eisen = self.eval_task_eisen.to_dict()

        eval_task_difficulty = self.eval_task_difficulty.to_dict()

        eval_task_generation_in_advance_days = self.eval_task_generation_in_advance_days.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eval_periods": eval_periods,
                "eval_approach": eval_approach,
                "eval_task_eisen": eval_task_eisen,
                "eval_task_difficulty": eval_task_difficulty,
                "eval_task_generation_in_advance_days": eval_task_generation_in_advance_days,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.life_plan_update_eval_settings_args_eval_approach import (
            LifePlanUpdateEvalSettingsArgsEvalApproach,  # noqa: PLC0415
        )
        from ..models.life_plan_update_eval_settings_args_eval_periods import LifePlanUpdateEvalSettingsArgsEvalPeriods  # noqa: PLC0415
        from ..models.life_plan_update_eval_settings_args_eval_task_difficulty import (
            LifePlanUpdateEvalSettingsArgsEvalTaskDifficulty,  # noqa: PLC0415
        )
        from ..models.life_plan_update_eval_settings_args_eval_task_eisen import (
            LifePlanUpdateEvalSettingsArgsEvalTaskEisen,  # noqa: PLC0415
        )
        from ..models.life_plan_update_eval_settings_args_eval_task_generation_in_advance_days import (
            LifePlanUpdateEvalSettingsArgsEvalTaskGenerationInAdvanceDays,  # noqa: PLC0415
        )
        from ..models.life_plan_update_eval_settings_args_schedulability import (
            LifePlanUpdateEvalSettingsArgsSchedulability,  # noqa: PLC0415
        )
        from ..models.life_plan_update_eval_settings_args_scheduling_event_count import (
            LifePlanUpdateEvalSettingsArgsSchedulingEventCount,  # noqa: PLC0415
        )
        from ..models.life_plan_update_eval_settings_args_scheduling_event_duration_mins import (
            LifePlanUpdateEvalSettingsArgsSchedulingEventDurationMins,  # noqa: PLC0415
        )

        d = dict(src_dict)
        eval_periods = LifePlanUpdateEvalSettingsArgsEvalPeriods.from_dict(d.pop("eval_periods"))

        eval_approach = LifePlanUpdateEvalSettingsArgsEvalApproach.from_dict(d.pop("eval_approach"))

        eval_task_eisen = LifePlanUpdateEvalSettingsArgsEvalTaskEisen.from_dict(d.pop("eval_task_eisen"))

        eval_task_difficulty = LifePlanUpdateEvalSettingsArgsEvalTaskDifficulty.from_dict(d.pop("eval_task_difficulty"))

        eval_task_generation_in_advance_days = LifePlanUpdateEvalSettingsArgsEvalTaskGenerationInAdvanceDays.from_dict(
            d.pop("eval_task_generation_in_advance_days")
        )

        schedulability = LifePlanUpdateEvalSettingsArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = LifePlanUpdateEvalSettingsArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = LifePlanUpdateEvalSettingsArgsSchedulingEventCount.from_dict(
            d.pop("scheduling_event_count")
        )

        life_plan_update_eval_settings_args = cls(
            eval_periods=eval_periods,
            eval_approach=eval_approach,
            eval_task_eisen=eval_task_eisen,
            eval_task_difficulty=eval_task_difficulty,
            eval_task_generation_in_advance_days=eval_task_generation_in_advance_days,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
        )

        life_plan_update_eval_settings_args.additional_properties = d
        return life_plan_update_eval_settings_args

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
