from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricFindArgs")


@_attrs_define
class MetricFindArgs:
    """PersonFindArgs.

    Attributes:
        allow_archived (bool):
        include_notes (bool):
        include_entries (bool):
        include_collection_inbox_tasks (bool):
        include_metric_entry_notes (bool):
        filter_ref_ids (Union[List[str], None, Unset]):
        filter_entry_ref_ids (Union[List[str], None, Unset]):
    """

    allow_archived: bool
    include_notes: bool
    include_entries: bool
    include_collection_inbox_tasks: bool
    include_metric_entry_notes: bool
    filter_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_entry_ref_ids: Union[List[str], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        include_entries = self.include_entries

        include_collection_inbox_tasks = self.include_collection_inbox_tasks

        include_metric_entry_notes = self.include_metric_entry_notes

        filter_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = UNSET
        elif isinstance(self.filter_ref_ids, list):
            filter_ref_ids = self.filter_ref_ids

        else:
            filter_ref_ids = self.filter_ref_ids

        filter_entry_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_entry_ref_ids, Unset):
            filter_entry_ref_ids = UNSET
        elif isinstance(self.filter_entry_ref_ids, list):
            filter_entry_ref_ids = self.filter_entry_ref_ids

        else:
            filter_entry_ref_ids = self.filter_entry_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_notes": include_notes,
                "include_entries": include_entries,
                "include_collection_inbox_tasks": include_collection_inbox_tasks,
                "include_metric_entry_notes": include_metric_entry_notes,
            }
        )
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids
        if filter_entry_ref_ids is not UNSET:
            field_dict["filter_entry_ref_ids"] = filter_entry_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        include_notes = d.pop("include_notes")

        include_entries = d.pop("include_entries")

        include_collection_inbox_tasks = d.pop("include_collection_inbox_tasks")

        include_metric_entry_notes = d.pop("include_metric_entry_notes")

        def _parse_filter_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_ref_ids_type_0 = cast(List[str], data)

                return filter_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_ref_ids = _parse_filter_ref_ids(d.pop("filter_ref_ids", UNSET))

        def _parse_filter_entry_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_entry_ref_ids_type_0 = cast(List[str], data)

                return filter_entry_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_entry_ref_ids = _parse_filter_entry_ref_ids(d.pop("filter_entry_ref_ids", UNSET))

        metric_find_args = cls(
            allow_archived=allow_archived,
            include_notes=include_notes,
            include_entries=include_entries,
            include_collection_inbox_tasks=include_collection_inbox_tasks,
            include_metric_entry_notes=include_metric_entry_notes,
            filter_ref_ids=filter_ref_ids,
            filter_entry_ref_ids=filter_entry_ref_ids,
        )

        metric_find_args.additional_properties = d
        return metric_find_args

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
