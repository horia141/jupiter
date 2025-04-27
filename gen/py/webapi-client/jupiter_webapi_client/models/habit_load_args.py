from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HabitLoadArgs")


@_attrs_define
class HabitLoadArgs:
    """HabitLoadArgs.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
        inbox_task_retrieve_offset (Union[None, Unset, int]):
        include_streak_marks_for_year (Union[None, Unset, int]):
    """

    ref_id: str
    allow_archived: bool
    inbox_task_retrieve_offset: Union[None, Unset, int] = UNSET
    include_streak_marks_for_year: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        inbox_task_retrieve_offset: Union[None, Unset, int]
        if isinstance(self.inbox_task_retrieve_offset, Unset):
            inbox_task_retrieve_offset = UNSET
        else:
            inbox_task_retrieve_offset = self.inbox_task_retrieve_offset

        include_streak_marks_for_year: Union[None, Unset, int]
        if isinstance(self.include_streak_marks_for_year, Unset):
            include_streak_marks_for_year = UNSET
        else:
            include_streak_marks_for_year = self.include_streak_marks_for_year

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
            }
        )
        if inbox_task_retrieve_offset is not UNSET:
            field_dict["inbox_task_retrieve_offset"] = inbox_task_retrieve_offset
        if include_streak_marks_for_year is not UNSET:
            field_dict["include_streak_marks_for_year"] = include_streak_marks_for_year

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        def _parse_inbox_task_retrieve_offset(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        inbox_task_retrieve_offset = _parse_inbox_task_retrieve_offset(d.pop("inbox_task_retrieve_offset", UNSET))

        def _parse_include_streak_marks_for_year(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        include_streak_marks_for_year = _parse_include_streak_marks_for_year(
            d.pop("include_streak_marks_for_year", UNSET)
        )

        habit_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
            inbox_task_retrieve_offset=inbox_task_retrieve_offset,
            include_streak_marks_for_year=include_streak_marks_for_year,
        )

        habit_load_args.additional_properties = d
        return habit_load_args

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
