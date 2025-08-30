from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.journal_generation_approach import JournalGenerationApproach
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.journal_load_settings_result_generation_in_advance_days import (
        JournalLoadSettingsResultGenerationInAdvanceDays,
    )
    from ..models.project import Project
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="JournalLoadSettingsResult")


@_attrs_define
class JournalLoadSettingsResult:
    """JournalLoadSettings results.

    Attributes:
        periods (list[RecurringTaskPeriod]):
        generation_approach (JournalGenerationApproach): The approach to generate journals.
        generation_in_advance_days (JournalLoadSettingsResultGenerationInAdvanceDays):
        writing_tasks (list['InboxTask']):
        writing_task_project (Union['Project', None, Unset]):
        writing_task_gen_params (Union['RecurringTaskGenParams', None, Unset]):
    """

    periods: list[RecurringTaskPeriod]
    generation_approach: JournalGenerationApproach
    generation_in_advance_days: "JournalLoadSettingsResultGenerationInAdvanceDays"
    writing_tasks: list["InboxTask"]
    writing_task_project: Union["Project", None, Unset] = UNSET
    writing_task_gen_params: Union["RecurringTaskGenParams", None, Unset] = UNSET
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

        writing_tasks = []
        for writing_tasks_item_data in self.writing_tasks:
            writing_tasks_item = writing_tasks_item_data.to_dict()
            writing_tasks.append(writing_tasks_item)

        writing_task_project: Union[None, Unset, dict[str, Any]]
        if isinstance(self.writing_task_project, Unset):
            writing_task_project = UNSET
        elif isinstance(self.writing_task_project, Project):
            writing_task_project = self.writing_task_project.to_dict()
        else:
            writing_task_project = self.writing_task_project

        writing_task_gen_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.writing_task_gen_params, Unset):
            writing_task_gen_params = UNSET
        elif isinstance(self.writing_task_gen_params, RecurringTaskGenParams):
            writing_task_gen_params = self.writing_task_gen_params.to_dict()
        else:
            writing_task_gen_params = self.writing_task_gen_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
                "generation_approach": generation_approach,
                "generation_in_advance_days": generation_in_advance_days,
                "writing_tasks": writing_tasks,
            }
        )
        if writing_task_project is not UNSET:
            field_dict["writing_task_project"] = writing_task_project
        if writing_task_gen_params is not UNSET:
            field_dict["writing_task_gen_params"] = writing_task_gen_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.journal_load_settings_result_generation_in_advance_days import (
            JournalLoadSettingsResultGenerationInAdvanceDays,
        )
        from ..models.project import Project
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = dict(src_dict)
        periods = []
        _periods = d.pop("periods")
        for periods_item_data in _periods:
            periods_item = RecurringTaskPeriod(periods_item_data)

            periods.append(periods_item)

        generation_approach = JournalGenerationApproach(d.pop("generation_approach"))

        generation_in_advance_days = JournalLoadSettingsResultGenerationInAdvanceDays.from_dict(
            d.pop("generation_in_advance_days")
        )

        writing_tasks = []
        _writing_tasks = d.pop("writing_tasks")
        for writing_tasks_item_data in _writing_tasks:
            writing_tasks_item = InboxTask.from_dict(writing_tasks_item_data)

            writing_tasks.append(writing_tasks_item)

        def _parse_writing_task_project(data: object) -> Union["Project", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                writing_task_project_type_0 = Project.from_dict(data)

                return writing_task_project_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Project", None, Unset], data)

        writing_task_project = _parse_writing_task_project(d.pop("writing_task_project", UNSET))

        def _parse_writing_task_gen_params(data: object) -> Union["RecurringTaskGenParams", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                writing_task_gen_params_type_0 = RecurringTaskGenParams.from_dict(data)

                return writing_task_gen_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RecurringTaskGenParams", None, Unset], data)

        writing_task_gen_params = _parse_writing_task_gen_params(d.pop("writing_task_gen_params", UNSET))

        journal_load_settings_result = cls(
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=generation_in_advance_days,
            writing_tasks=writing_tasks,
            writing_task_project=writing_task_project,
            writing_task_gen_params=writing_task_gen_params,
        )

        journal_load_settings_result.additional_properties = d
        return journal_load_settings_result

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
