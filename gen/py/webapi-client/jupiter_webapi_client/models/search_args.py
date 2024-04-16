from typing import Any, Dict, List, Type, TypeVar, Union

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
        filter_entity_tags (Union[Unset, List[NamedEntityTag]]):
        filter_created_time_after (Union[Unset, str]): A date or possibly a datetime for the application.
        filter_created_time_before (Union[Unset, str]): A date or possibly a datetime for the application.
        filter_last_modified_time_after (Union[Unset, str]): A date or possibly a datetime for the application.
        filter_last_modified_time_before (Union[Unset, str]): A date or possibly a datetime for the application.
        filter_archived_time_after (Union[Unset, str]): A date or possibly a datetime for the application.
        filter_archived_time_before (Union[Unset, str]): A date or possibly a datetime for the application.
    """

    query: str
    limit: int
    include_archived: bool
    filter_entity_tags: Union[Unset, List[NamedEntityTag]] = UNSET
    filter_created_time_after: Union[Unset, str] = UNSET
    filter_created_time_before: Union[Unset, str] = UNSET
    filter_last_modified_time_after: Union[Unset, str] = UNSET
    filter_last_modified_time_before: Union[Unset, str] = UNSET
    filter_archived_time_after: Union[Unset, str] = UNSET
    filter_archived_time_before: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        query = self.query

        limit = self.limit

        include_archived = self.include_archived

        filter_entity_tags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_entity_tags, Unset):
            filter_entity_tags = []
            for filter_entity_tags_item_data in self.filter_entity_tags:
                filter_entity_tags_item = filter_entity_tags_item_data.value
                filter_entity_tags.append(filter_entity_tags_item)

        filter_created_time_after = self.filter_created_time_after

        filter_created_time_before = self.filter_created_time_before

        filter_last_modified_time_after = self.filter_last_modified_time_after

        filter_last_modified_time_before = self.filter_last_modified_time_before

        filter_archived_time_after = self.filter_archived_time_after

        filter_archived_time_before = self.filter_archived_time_before

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        query = d.pop("query")

        limit = d.pop("limit")

        include_archived = d.pop("include_archived")

        filter_entity_tags = []
        _filter_entity_tags = d.pop("filter_entity_tags", UNSET)
        for filter_entity_tags_item_data in _filter_entity_tags or []:
            filter_entity_tags_item = NamedEntityTag(filter_entity_tags_item_data)

            filter_entity_tags.append(filter_entity_tags_item)

        filter_created_time_after = d.pop("filter_created_time_after", UNSET)

        filter_created_time_before = d.pop("filter_created_time_before", UNSET)

        filter_last_modified_time_after = d.pop("filter_last_modified_time_after", UNSET)

        filter_last_modified_time_before = d.pop("filter_last_modified_time_before", UNSET)

        filter_archived_time_after = d.pop("filter_archived_time_after", UNSET)

        filter_archived_time_before = d.pop("filter_archived_time_before", UNSET)

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
