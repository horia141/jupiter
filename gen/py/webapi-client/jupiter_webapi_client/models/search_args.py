from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.named_entity_tag import NamedEntityTag
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchArgs")


@_attrs_define
class SearchArgs:
    """Search args.

    Attributes:
        query (str): A search query parameter for searches.
        limit (int): A search limit parameter for searches.
        include_archived (bool):
        filter_entity_tags (Union[None, Unset, list[NamedEntityTag]]):
        filter_created_time_after (Union[None, Unset, str]):
        filter_created_time_before (Union[None, Unset, str]):
        filter_last_modified_time_after (Union[None, Unset, str]):
        filter_last_modified_time_before (Union[None, Unset, str]):
        filter_archived_time_after (Union[None, Unset, str]):
        filter_archived_time_before (Union[None, Unset, str]):
    """

    query: str
    limit: int
    include_archived: bool
    filter_entity_tags: Union[None, Unset, list[NamedEntityTag]] = UNSET
    filter_created_time_after: Union[None, Unset, str] = UNSET
    filter_created_time_before: Union[None, Unset, str] = UNSET
    filter_last_modified_time_after: Union[None, Unset, str] = UNSET
    filter_last_modified_time_before: Union[None, Unset, str] = UNSET
    filter_archived_time_after: Union[None, Unset, str] = UNSET
    filter_archived_time_before: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        limit = self.limit

        include_archived = self.include_archived

        filter_entity_tags: Union[None, Unset, list[str]]
        if isinstance(self.filter_entity_tags, Unset):
            filter_entity_tags = UNSET
        elif isinstance(self.filter_entity_tags, list):
            filter_entity_tags = []
            for filter_entity_tags_type_0_item_data in self.filter_entity_tags:
                filter_entity_tags_type_0_item = filter_entity_tags_type_0_item_data.value
                filter_entity_tags.append(filter_entity_tags_type_0_item)

        else:
            filter_entity_tags = self.filter_entity_tags

        filter_created_time_after: Union[None, Unset, str]
        if isinstance(self.filter_created_time_after, Unset):
            filter_created_time_after = UNSET
        else:
            filter_created_time_after = self.filter_created_time_after

        filter_created_time_before: Union[None, Unset, str]
        if isinstance(self.filter_created_time_before, Unset):
            filter_created_time_before = UNSET
        else:
            filter_created_time_before = self.filter_created_time_before

        filter_last_modified_time_after: Union[None, Unset, str]
        if isinstance(self.filter_last_modified_time_after, Unset):
            filter_last_modified_time_after = UNSET
        else:
            filter_last_modified_time_after = self.filter_last_modified_time_after

        filter_last_modified_time_before: Union[None, Unset, str]
        if isinstance(self.filter_last_modified_time_before, Unset):
            filter_last_modified_time_before = UNSET
        else:
            filter_last_modified_time_before = self.filter_last_modified_time_before

        filter_archived_time_after: Union[None, Unset, str]
        if isinstance(self.filter_archived_time_after, Unset):
            filter_archived_time_after = UNSET
        else:
            filter_archived_time_after = self.filter_archived_time_after

        filter_archived_time_before: Union[None, Unset, str]
        if isinstance(self.filter_archived_time_before, Unset):
            filter_archived_time_before = UNSET
        else:
            filter_archived_time_before = self.filter_archived_time_before

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
                "limit": limit,
                "include_archived": include_archived,
            }
        )
        if filter_entity_tags is not UNSET:
            field_dict["filter_entity_tags"] = filter_entity_tags
        if filter_created_time_after is not UNSET:
            field_dict["filter_created_time_after"] = filter_created_time_after
        if filter_created_time_before is not UNSET:
            field_dict["filter_created_time_before"] = filter_created_time_before
        if filter_last_modified_time_after is not UNSET:
            field_dict["filter_last_modified_time_after"] = filter_last_modified_time_after
        if filter_last_modified_time_before is not UNSET:
            field_dict["filter_last_modified_time_before"] = filter_last_modified_time_before
        if filter_archived_time_after is not UNSET:
            field_dict["filter_archived_time_after"] = filter_archived_time_after
        if filter_archived_time_before is not UNSET:
            field_dict["filter_archived_time_before"] = filter_archived_time_before

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        limit = d.pop("limit")

        include_archived = d.pop("include_archived")

        def _parse_filter_entity_tags(data: object) -> Union[None, Unset, list[NamedEntityTag]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_entity_tags_type_0 = []
                _filter_entity_tags_type_0 = data
                for filter_entity_tags_type_0_item_data in _filter_entity_tags_type_0:
                    filter_entity_tags_type_0_item = NamedEntityTag(filter_entity_tags_type_0_item_data)

                    filter_entity_tags_type_0.append(filter_entity_tags_type_0_item)

                return filter_entity_tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[NamedEntityTag]], data)

        filter_entity_tags = _parse_filter_entity_tags(d.pop("filter_entity_tags", UNSET))

        def _parse_filter_created_time_after(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filter_created_time_after = _parse_filter_created_time_after(d.pop("filter_created_time_after", UNSET))

        def _parse_filter_created_time_before(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filter_created_time_before = _parse_filter_created_time_before(d.pop("filter_created_time_before", UNSET))

        def _parse_filter_last_modified_time_after(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filter_last_modified_time_after = _parse_filter_last_modified_time_after(
            d.pop("filter_last_modified_time_after", UNSET)
        )

        def _parse_filter_last_modified_time_before(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filter_last_modified_time_before = _parse_filter_last_modified_time_before(
            d.pop("filter_last_modified_time_before", UNSET)
        )

        def _parse_filter_archived_time_after(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filter_archived_time_after = _parse_filter_archived_time_after(d.pop("filter_archived_time_after", UNSET))

        def _parse_filter_archived_time_before(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filter_archived_time_before = _parse_filter_archived_time_before(d.pop("filter_archived_time_before", UNSET))

        search_args = cls(
            query=query,
            limit=limit,
            include_archived=include_archived,
            filter_entity_tags=filter_entity_tags,
            filter_created_time_after=filter_created_time_after,
            filter_created_time_before=filter_created_time_before,
            filter_last_modified_time_after=filter_last_modified_time_after,
            filter_last_modified_time_before=filter_last_modified_time_before,
            filter_archived_time_after=filter_archived_time_after,
            filter_archived_time_before=filter_archived_time_before,
        )

        search_args.additional_properties = d
        return search_args

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
