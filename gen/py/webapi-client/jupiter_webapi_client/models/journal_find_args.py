from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalFindArgs")


@_attrs_define
class JournalFindArgs:
    """Args.

    Attributes:
        allow_archived (bool):
        include_notes (bool):
        include_writing_tasks (bool):
        filter_ref_ids (Union[Unset, List[str]]):
    """

    allow_archived: bool
    include_notes: bool
    include_writing_tasks: bool
    filter_ref_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        include_writing_tasks = self.include_writing_tasks

        filter_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = self.filter_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_notes": include_notes,
                "include_writing_tasks": include_writing_tasks,
            }
        )
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        include_notes = d.pop("include_notes")

        include_writing_tasks = d.pop("include_writing_tasks")

        filter_ref_ids = cast(List[str], d.pop("filter_ref_ids", UNSET))

        journal_find_args = cls(
            allow_archived=allow_archived,
            include_notes=include_notes,
            include_writing_tasks=include_writing_tasks,
            filter_ref_ids=filter_ref_ids,
        )

        journal_find_args.additional_properties = d
        return journal_find_args

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
