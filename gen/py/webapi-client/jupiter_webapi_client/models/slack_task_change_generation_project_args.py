from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SlackTaskChangeGenerationProjectArgs")


@_attrs_define
class SlackTaskChangeGenerationProjectArgs:
    """PersonFindArgs.

    Attributes:
        generation_project_ref_id (str): A generic entity id.
    """

    generation_project_ref_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation_project_ref_id = self.generation_project_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_project_ref_id": generation_project_ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        generation_project_ref_id = d.pop("generation_project_ref_id")

        slack_task_change_generation_project_args = cls(
            generation_project_ref_id=generation_project_ref_id,
        )

        slack_task_change_generation_project_args.additional_properties = d
        return slack_task_change_generation_project_args

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
