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
        filter_ref_ids (Union[List[str], None, Unset]):
        filter_project_ref_ids (Union[List[str], None, Unset]):
        filter_sources (Union[List[InboxTaskSource], None, Unset]):
    """

    allow_archived: bool
    include_notes: bool
    filter_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_project_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_sources: Union[List[InboxTaskSource], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        filter_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = UNSET
        elif isinstance(self.filter_ref_ids, list):
            filter_ref_ids = self.filter_ref_ids

        else:
            filter_ref_ids = self.filter_ref_ids

        filter_project_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = UNSET
        elif isinstance(self.filter_project_ref_ids, list):
            filter_project_ref_ids = self.filter_project_ref_ids

        else:
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_sources: Union[List[str], None, Unset]
        if isinstance(self.filter_sources, Unset):
            filter_sources = UNSET
        elif isinstance(self.filter_sources, list):
            filter_sources = []
            for filter_sources_type_0_item_data in self.filter_sources:
                filter_sources_type_0_item = filter_sources_type_0_item_data.value
                filter_sources.append(filter_sources_type_0_item)

        else:
            filter_sources = self.filter_sources

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

        def _parse_filter_project_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_project_ref_ids_type_0 = cast(List[str], data)

                return filter_project_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_project_ref_ids = _parse_filter_project_ref_ids(d.pop("filter_project_ref_ids", UNSET))

        def _parse_filter_sources(data: object) -> Union[List[InboxTaskSource], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_sources_type_0 = []
                _filter_sources_type_0 = data
                for filter_sources_type_0_item_data in _filter_sources_type_0:
                    filter_sources_type_0_item = InboxTaskSource(filter_sources_type_0_item_data)

                    filter_sources_type_0.append(filter_sources_type_0_item)

                return filter_sources_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[InboxTaskSource], None, Unset], data)

        filter_sources = _parse_filter_sources(d.pop("filter_sources", UNSET))

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
