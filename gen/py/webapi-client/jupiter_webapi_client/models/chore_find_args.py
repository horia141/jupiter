from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChoreFindArgs")


@_attrs_define
class ChoreFindArgs:
    """PersonFindArgs.

    Attributes:
        allow_archived (bool):
        include_project (bool):
        include_inbox_tasks (bool):
        include_notes (bool):
        filter_ref_ids (Union[Unset, List[str]]):
        filter_project_ref_ids (Union[Unset, List[str]]):
    """

    allow_archived: bool
    include_project: bool
    include_inbox_tasks: bool
    include_notes: bool
    filter_ref_ids: Union[Unset, List[str]] = UNSET
    filter_project_ref_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_project = self.include_project

        include_inbox_tasks = self.include_inbox_tasks

        include_notes = self.include_notes

        filter_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = self.filter_ref_ids

        filter_project_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = self.filter_project_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_project": include_project,
                "include_inbox_tasks": include_inbox_tasks,
                "include_notes": include_notes,
            }
        )
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids
        if filter_project_ref_ids is not UNSET:
            field_dict["filter_project_ref_ids"] = filter_project_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        include_project = d.pop("include_project")

        include_inbox_tasks = d.pop("include_inbox_tasks")

        include_notes = d.pop("include_notes")

        filter_ref_ids = cast(List[str], d.pop("filter_ref_ids", UNSET))

        filter_project_ref_ids = cast(List[str], d.pop("filter_project_ref_ids", UNSET))

        chore_find_args = cls(
            allow_archived=allow_archived,
            include_project=include_project,
            include_inbox_tasks=include_inbox_tasks,
            include_notes=include_notes,
            filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids,
        )

        chore_find_args.additional_properties = d
        return chore_find_args

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
