from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonFindArgs")


@_attrs_define
class PersonFindArgs:
    """PersonFindArgs.

    Attributes:
        allow_archived (bool):
        include_catch_up_inbox_tasks (bool):
        include_birthday_inbox_tasks (bool):
        include_notes (bool):
        filter_person_ref_ids (Union[List[str], None, Unset]):
    """

    allow_archived: bool
    include_catch_up_inbox_tasks: bool
    include_birthday_inbox_tasks: bool
    include_notes: bool
    filter_person_ref_ids: Union[List[str], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_catch_up_inbox_tasks = self.include_catch_up_inbox_tasks

        include_birthday_inbox_tasks = self.include_birthday_inbox_tasks

        include_notes = self.include_notes

        filter_person_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_person_ref_ids, Unset):
            filter_person_ref_ids = UNSET
        elif isinstance(self.filter_person_ref_ids, list):
            filter_person_ref_ids = self.filter_person_ref_ids

        else:
            filter_person_ref_ids = self.filter_person_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_catch_up_inbox_tasks": include_catch_up_inbox_tasks,
                "include_birthday_inbox_tasks": include_birthday_inbox_tasks,
                "include_notes": include_notes,
            }
        )
        if filter_person_ref_ids is not UNSET:
            field_dict["filter_person_ref_ids"] = filter_person_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        include_catch_up_inbox_tasks = d.pop("include_catch_up_inbox_tasks")

        include_birthday_inbox_tasks = d.pop("include_birthday_inbox_tasks")

        include_notes = d.pop("include_notes")

        def _parse_filter_person_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_person_ref_ids_type_0 = cast(List[str], data)

                return filter_person_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_person_ref_ids = _parse_filter_person_ref_ids(d.pop("filter_person_ref_ids", UNSET))

        person_find_args = cls(
            allow_archived=allow_archived,
            include_catch_up_inbox_tasks=include_catch_up_inbox_tasks,
            include_birthday_inbox_tasks=include_birthday_inbox_tasks,
            include_notes=include_notes,
            filter_person_ref_ids=filter_person_ref_ids,
        )

        person_find_args.additional_properties = d
        return person_find_args

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
