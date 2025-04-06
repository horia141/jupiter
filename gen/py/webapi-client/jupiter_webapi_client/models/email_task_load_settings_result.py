from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.project import Project


T = TypeVar("T", bound="EmailTaskLoadSettingsResult")


@_attrs_define
class EmailTaskLoadSettingsResult:
    """EmailTaskLoadSettings results.

    Attributes:
        generation_project (Project): The project.
    """

    generation_project: "Project"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation_project = self.generation_project.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_project": generation_project,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project import Project

        d = dict(src_dict)
        generation_project = Project.from_dict(d.pop("generation_project"))

        email_task_load_settings_result = cls(
            generation_project=generation_project,
        )

        email_task_load_settings_result.additional_properties = d
        return email_task_load_settings_result

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
