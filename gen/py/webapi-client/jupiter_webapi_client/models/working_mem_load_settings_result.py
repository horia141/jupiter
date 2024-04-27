from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

if TYPE_CHECKING:
    from ..models.project import Project


T = TypeVar("T", bound="WorkingMemLoadSettingsResult")


@_attrs_define
class WorkingMemLoadSettingsResult:
    """WorkingMemLoadSettings results.

    Attributes:
        generation_period (RecurringTaskPeriod): A period for a particular task.
        cleanup_project (Project): The project.
    """

    generation_period: RecurringTaskPeriod
    cleanup_project: "Project"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        generation_period = self.generation_period.value

        cleanup_project = self.cleanup_project.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_period": generation_period,
                "cleanup_project": cleanup_project,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project import Project

        d = src_dict.copy()
        generation_period = RecurringTaskPeriod(d.pop("generation_period"))

        cleanup_project = Project.from_dict(d.pop("cleanup_project"))

        working_mem_load_settings_result = cls(
            generation_period=generation_period,
            cleanup_project=cleanup_project,
        )

        working_mem_load_settings_result.additional_properties = d
        return working_mem_load_settings_result

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
