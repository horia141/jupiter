from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.inbox_task_source import InboxTaskSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="InboxTaskFindArgs")


@_attrs_define
class InboxTaskFindArgs:
    """PersonFindArgs.

    Attributes:
        allow_archived (bool):
        include_notes (bool):
        filter_ref_ids (Union[Unset, List[str]]):
        filter_project_ref_ids (Union[Unset, List[str]]):
        filter_sources (Union[Unset, List[InboxTaskSource]]):
    """

    allow_archived: bool
    include_notes: bool
    filter_ref_ids: Union[Unset, List[str]] = UNSET
    filter_project_ref_ids: Union[Unset, List[str]] = UNSET
    filter_sources: Union[Unset, List[InboxTaskSource]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        filter_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = self.filter_ref_ids

        filter_project_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_sources: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_sources, Unset):
            filter_sources = []
            for filter_sources_item_data in self.filter_sources:
                filter_sources_item = filter_sources_item_data.value
                filter_sources.append(filter_sources_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_notes": include_notes,
            }
        )
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids
        if filter_project_ref_ids is not UNSET:
            field_dict["filter_project_ref_ids"] = filter_project_ref_ids
        if filter_sources is not UNSET:
            field_dict["filter_sources"] = filter_sources

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        include_notes = d.pop("include_notes")

        filter_ref_ids = cast(List[str], d.pop("filter_ref_ids", UNSET))

        filter_project_ref_ids = cast(List[str], d.pop("filter_project_ref_ids", UNSET))

        filter_sources = []
        _filter_sources = d.pop("filter_sources", UNSET)
        for filter_sources_item_data in _filter_sources or []:
            filter_sources_item = InboxTaskSource(filter_sources_item_data)

            filter_sources.append(filter_sources_item)

        inbox_task_find_args = cls(
            allow_archived=allow_archived,
            include_notes=include_notes,
            filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_sources=filter_sources,
        )

        inbox_task_find_args.additional_properties = d
        return inbox_task_find_args

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
