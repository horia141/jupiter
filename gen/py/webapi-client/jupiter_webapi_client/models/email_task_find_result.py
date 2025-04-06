from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.email_task_find_result_entry import EmailTaskFindResultEntry
    from ..models.project import Project


T = TypeVar("T", bound="EmailTaskFindResult")


@_attrs_define
class EmailTaskFindResult:
    """PersonFindResult.

    Attributes:
        generation_project (Project): The project.
        entries (list['EmailTaskFindResultEntry']):
    """

    generation_project: "Project"
    entries: list["EmailTaskFindResultEntry"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation_project = self.generation_project.to_dict()

        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_project": generation_project,
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_task_find_result_entry import EmailTaskFindResultEntry
        from ..models.project import Project

        d = dict(src_dict)
        generation_project = Project.from_dict(d.pop("generation_project"))

        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = EmailTaskFindResultEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        email_task_find_result = cls(
            generation_project=generation_project,
            entries=entries,
        )

        email_task_find_result.additional_properties = d
        return email_task_find_result

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
