from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

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
        include_time_event_blocks (bool):
        filter_just_workable (Union[None, Unset, bool]):
        filter_just_generated (Union[None, Unset, bool]):
        filter_ref_ids (Union[None, Unset, list[str]]):
        filter_project_ref_ids (Union[None, Unset, list[str]]):
        filter_sources (Union[None, Unset, list[InboxTaskSource]]):
        filter_source_entity_ref_ids (Union[None, Unset, list[str]]):
    """

    allow_archived: bool
    include_notes: bool
    include_time_event_blocks: bool
    filter_just_workable: Union[None, Unset, bool] = UNSET
    filter_just_generated: Union[None, Unset, bool] = UNSET
    filter_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_project_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_sources: Union[None, Unset, list[InboxTaskSource]] = UNSET
    filter_source_entity_ref_ids: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        include_time_event_blocks = self.include_time_event_blocks

        filter_just_workable: Union[None, Unset, bool]
        if isinstance(self.filter_just_workable, Unset):
            filter_just_workable = UNSET
        else:
            filter_just_workable = self.filter_just_workable

        filter_just_generated: Union[None, Unset, bool]
        if isinstance(self.filter_just_generated, Unset):
            filter_just_generated = UNSET
        else:
            filter_just_generated = self.filter_just_generated

        filter_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = UNSET
        elif isinstance(self.filter_ref_ids, list):
            filter_ref_ids = self.filter_ref_ids

        else:
            filter_ref_ids = self.filter_ref_ids

        filter_project_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = UNSET
        elif isinstance(self.filter_project_ref_ids, list):
            filter_project_ref_ids = self.filter_project_ref_ids

        else:
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_sources: Union[None, Unset, list[str]]
        if isinstance(self.filter_sources, Unset):
            filter_sources = UNSET
        elif isinstance(self.filter_sources, list):
            filter_sources = []
            for filter_sources_type_0_item_data in self.filter_sources:
                filter_sources_type_0_item = filter_sources_type_0_item_data.value
                filter_sources.append(filter_sources_type_0_item)

        else:
            filter_sources = self.filter_sources

        filter_source_entity_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_source_entity_ref_ids, Unset):
            filter_source_entity_ref_ids = UNSET
        elif isinstance(self.filter_source_entity_ref_ids, list):
            filter_source_entity_ref_ids = self.filter_source_entity_ref_ids

        else:
            filter_source_entity_ref_ids = self.filter_source_entity_ref_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_notes": include_notes,
                "include_time_event_blocks": include_time_event_blocks,
            }
        )
        if filter_just_workable is not UNSET:
            field_dict["filter_just_workable"] = filter_just_workable
        if filter_just_generated is not UNSET:
            field_dict["filter_just_generated"] = filter_just_generated
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids
        if filter_project_ref_ids is not UNSET:
            field_dict["filter_project_ref_ids"] = filter_project_ref_ids
        if filter_sources is not UNSET:
            field_dict["filter_sources"] = filter_sources
        if filter_source_entity_ref_ids is not UNSET:
            field_dict["filter_source_entity_ref_ids"] = filter_source_entity_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_archived = d.pop("allow_archived")

        include_notes = d.pop("include_notes")

        include_time_event_blocks = d.pop("include_time_event_blocks")

        def _parse_filter_just_workable(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        filter_just_workable = _parse_filter_just_workable(d.pop("filter_just_workable", UNSET))

        def _parse_filter_just_generated(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        filter_just_generated = _parse_filter_just_generated(d.pop("filter_just_generated", UNSET))

        def _parse_filter_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_ref_ids_type_0 = cast(list[str], data)

                return filter_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_ref_ids = _parse_filter_ref_ids(d.pop("filter_ref_ids", UNSET))

        def _parse_filter_project_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_project_ref_ids_type_0 = cast(list[str], data)

                return filter_project_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_project_ref_ids = _parse_filter_project_ref_ids(d.pop("filter_project_ref_ids", UNSET))

        def _parse_filter_sources(data: object) -> Union[None, Unset, list[InboxTaskSource]]:
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
            return cast(Union[None, Unset, list[InboxTaskSource]], data)

        filter_sources = _parse_filter_sources(d.pop("filter_sources", UNSET))

        def _parse_filter_source_entity_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_source_entity_ref_ids_type_0 = cast(list[str], data)

                return filter_source_entity_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_source_entity_ref_ids = _parse_filter_source_entity_ref_ids(d.pop("filter_source_entity_ref_ids", UNSET))

        inbox_task_find_args = cls(
            allow_archived=allow_archived,
            include_notes=include_notes,
            include_time_event_blocks=include_time_event_blocks,
            filter_just_workable=filter_just_workable,
            filter_just_generated=filter_just_generated,
            filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_sources=filter_sources,
            filter_source_entity_ref_ids=filter_source_entity_ref_ids,
        )

        inbox_task_find_args.additional_properties = d
        return inbox_task_find_args

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
