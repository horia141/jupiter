from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

if TYPE_CHECKING:
    from ..models.project import Project
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="JournalLoadSettingsResult")


@_attrs_define
class JournalLoadSettingsResult:
    """JournalLoadSettings results.

    Attributes:
        periods (List[RecurringTaskPeriod]):
        writing_task_project (Project): The project.
        writing_task_gen_params (RecurringTaskGenParams): Parameters for metric collection.
    """

    periods: List[RecurringTaskPeriod]
    writing_task_project: "Project"
    writing_task_gen_params: "RecurringTaskGenParams"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        periods = []
        for periods_item_data in self.periods:
            periods_item = periods_item_data.value
            periods.append(periods_item)

        writing_task_project = self.writing_task_project.to_dict()

        writing_task_gen_params = self.writing_task_gen_params.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
                "writing_task_project": writing_task_project,
                "writing_task_gen_params": writing_task_gen_params,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project import Project
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = src_dict.copy()
        periods = []
        _periods = d.pop("periods")
        for periods_item_data in _periods:
            periods_item = RecurringTaskPeriod(periods_item_data)

            periods.append(periods_item)

        writing_task_project = Project.from_dict(d.pop("writing_task_project"))

        writing_task_gen_params = RecurringTaskGenParams.from_dict(d.pop("writing_task_gen_params"))

        journal_load_settings_result = cls(
            periods=periods,
            writing_task_project=writing_task_project,
            writing_task_gen_params=writing_task_gen_params,
        )

        journal_load_settings_result.additional_properties = d
        return journal_load_settings_result

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
