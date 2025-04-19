from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_plan_update_settings_args_generation_approach import TimePlanUpdateSettingsArgsGenerationApproach
    from ..models.time_plan_update_settings_args_generation_in_advance_days import (
        TimePlanUpdateSettingsArgsGenerationInAdvanceDays,
    )
    from ..models.time_plan_update_settings_args_periods import TimePlanUpdateSettingsArgsPeriods
    from ..models.time_plan_update_settings_args_planning_task_difficulty import (
        TimePlanUpdateSettingsArgsPlanningTaskDifficulty,
    )
    from ..models.time_plan_update_settings_args_planning_task_eisen import TimePlanUpdateSettingsArgsPlanningTaskEisen
    from ..models.time_plan_update_settings_args_planning_task_project_ref_id import (
        TimePlanUpdateSettingsArgsPlanningTaskProjectRefId,
    )


T = TypeVar("T", bound="TimePlanUpdateSettingsArgs")


@_attrs_define
class TimePlanUpdateSettingsArgs:
    """Args.

    Attributes:
        periods (TimePlanUpdateSettingsArgsPeriods):
        generation_approach (TimePlanUpdateSettingsArgsGenerationApproach):
        generation_in_advance_days (TimePlanUpdateSettingsArgsGenerationInAdvanceDays):
        planning_task_project_ref_id (TimePlanUpdateSettingsArgsPlanningTaskProjectRefId):
        planning_task_eisen (TimePlanUpdateSettingsArgsPlanningTaskEisen):
        planning_task_difficulty (TimePlanUpdateSettingsArgsPlanningTaskDifficulty):
    """

    periods: "TimePlanUpdateSettingsArgsPeriods"
    generation_approach: "TimePlanUpdateSettingsArgsGenerationApproach"
    generation_in_advance_days: "TimePlanUpdateSettingsArgsGenerationInAdvanceDays"
    planning_task_project_ref_id: "TimePlanUpdateSettingsArgsPlanningTaskProjectRefId"
    planning_task_eisen: "TimePlanUpdateSettingsArgsPlanningTaskEisen"
    planning_task_difficulty: "TimePlanUpdateSettingsArgsPlanningTaskDifficulty"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        periods = self.periods.to_dict()

        generation_approach = self.generation_approach.to_dict()

        generation_in_advance_days = self.generation_in_advance_days.to_dict()

        planning_task_project_ref_id = self.planning_task_project_ref_id.to_dict()

        planning_task_eisen = self.planning_task_eisen.to_dict()

        planning_task_difficulty = self.planning_task_difficulty.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
                "generation_approach": generation_approach,
                "generation_in_advance_days": generation_in_advance_days,
                "planning_task_project_ref_id": planning_task_project_ref_id,
                "planning_task_eisen": planning_task_eisen,
                "planning_task_difficulty": planning_task_difficulty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_plan_update_settings_args_generation_approach import (
            TimePlanUpdateSettingsArgsGenerationApproach,
        )
        from ..models.time_plan_update_settings_args_generation_in_advance_days import (
            TimePlanUpdateSettingsArgsGenerationInAdvanceDays,
        )
        from ..models.time_plan_update_settings_args_periods import TimePlanUpdateSettingsArgsPeriods
        from ..models.time_plan_update_settings_args_planning_task_difficulty import (
            TimePlanUpdateSettingsArgsPlanningTaskDifficulty,
        )
        from ..models.time_plan_update_settings_args_planning_task_eisen import (
            TimePlanUpdateSettingsArgsPlanningTaskEisen,
        )
        from ..models.time_plan_update_settings_args_planning_task_project_ref_id import (
            TimePlanUpdateSettingsArgsPlanningTaskProjectRefId,
        )

        d = dict(src_dict)
        periods = TimePlanUpdateSettingsArgsPeriods.from_dict(d.pop("periods"))

        generation_approach = TimePlanUpdateSettingsArgsGenerationApproach.from_dict(d.pop("generation_approach"))

        generation_in_advance_days = TimePlanUpdateSettingsArgsGenerationInAdvanceDays.from_dict(
            d.pop("generation_in_advance_days")
        )

        planning_task_project_ref_id = TimePlanUpdateSettingsArgsPlanningTaskProjectRefId.from_dict(
            d.pop("planning_task_project_ref_id")
        )

        planning_task_eisen = TimePlanUpdateSettingsArgsPlanningTaskEisen.from_dict(d.pop("planning_task_eisen"))

        planning_task_difficulty = TimePlanUpdateSettingsArgsPlanningTaskDifficulty.from_dict(
            d.pop("planning_task_difficulty")
        )

        time_plan_update_settings_args = cls(
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=generation_in_advance_days,
            planning_task_project_ref_id=planning_task_project_ref_id,
            planning_task_eisen=planning_task_eisen,
            planning_task_difficulty=planning_task_difficulty,
        )

        time_plan_update_settings_args.additional_properties = d
        return time_plan_update_settings_args

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
