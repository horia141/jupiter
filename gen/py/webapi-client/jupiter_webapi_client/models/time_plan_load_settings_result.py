from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.time_plan_generation_approach import TimePlanGenerationApproach
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.project import Project
    from ..models.recurring_task_gen_params import RecurringTaskGenParams
    from ..models.time_plan_load_settings_result_generation_in_advance_days import (
        TimePlanLoadSettingsResultGenerationInAdvanceDays,
    )


T = TypeVar("T", bound="TimePlanLoadSettingsResult")


@_attrs_define
class TimePlanLoadSettingsResult:
    """TimePlanLoadSettingsResult.

    Attributes:
        periods (list[RecurringTaskPeriod]):
        generation_approach (TimePlanGenerationApproach): The approach to generate time plans.
        generation_in_advance_days (TimePlanLoadSettingsResultGenerationInAdvanceDays):
        planning_task_project (Union['Project', None, Unset]):
        planning_task_gen_params (Union['RecurringTaskGenParams', None, Unset]):
    """

    periods: list[RecurringTaskPeriod]
    generation_approach: TimePlanGenerationApproach
    generation_in_advance_days: "TimePlanLoadSettingsResultGenerationInAdvanceDays"
    planning_task_project: Union["Project", None, Unset] = UNSET
    planning_task_gen_params: Union["RecurringTaskGenParams", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.project import Project
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        periods = []
        for periods_item_data in self.periods:
            periods_item = periods_item_data.value
            periods.append(periods_item)

        generation_approach = self.generation_approach.value

        generation_in_advance_days = self.generation_in_advance_days.to_dict()

        planning_task_project: Union[None, Unset, dict[str, Any]]
        if isinstance(self.planning_task_project, Unset):
            planning_task_project = UNSET
        elif isinstance(self.planning_task_project, Project):
            planning_task_project = self.planning_task_project.to_dict()
        else:
            planning_task_project = self.planning_task_project

        planning_task_gen_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.planning_task_gen_params, Unset):
            planning_task_gen_params = UNSET
        elif isinstance(self.planning_task_gen_params, RecurringTaskGenParams):
            planning_task_gen_params = self.planning_task_gen_params.to_dict()
        else:
            planning_task_gen_params = self.planning_task_gen_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
                "generation_approach": generation_approach,
                "generation_in_advance_days": generation_in_advance_days,
            }
        )
        if planning_task_project is not UNSET:
            field_dict["planning_task_project"] = planning_task_project
        if planning_task_gen_params is not UNSET:
            field_dict["planning_task_gen_params"] = planning_task_gen_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project import Project
        from ..models.recurring_task_gen_params import RecurringTaskGenParams
        from ..models.time_plan_load_settings_result_generation_in_advance_days import (
            TimePlanLoadSettingsResultGenerationInAdvanceDays,
        )

        d = dict(src_dict)
        periods = []
        _periods = d.pop("periods")
        for periods_item_data in _periods:
            periods_item = RecurringTaskPeriod(periods_item_data)

            periods.append(periods_item)

        generation_approach = TimePlanGenerationApproach(d.pop("generation_approach"))

        generation_in_advance_days = TimePlanLoadSettingsResultGenerationInAdvanceDays.from_dict(
            d.pop("generation_in_advance_days")
        )

        def _parse_planning_task_project(data: object) -> Union["Project", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                planning_task_project_type_0 = Project.from_dict(data)

                return planning_task_project_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Project", None, Unset], data)

        planning_task_project = _parse_planning_task_project(d.pop("planning_task_project", UNSET))

        def _parse_planning_task_gen_params(data: object) -> Union["RecurringTaskGenParams", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                planning_task_gen_params_type_0 = RecurringTaskGenParams.from_dict(data)

                return planning_task_gen_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RecurringTaskGenParams", None, Unset], data)

        planning_task_gen_params = _parse_planning_task_gen_params(d.pop("planning_task_gen_params", UNSET))

        time_plan_load_settings_result = cls(
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=generation_in_advance_days,
            planning_task_project=planning_task_project,
            planning_task_gen_params=planning_task_gen_params,
        )

        time_plan_load_settings_result.additional_properties = d
        return time_plan_load_settings_result

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
