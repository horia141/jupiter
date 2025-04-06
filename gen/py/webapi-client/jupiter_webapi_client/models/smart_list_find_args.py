from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SmartListFindArgs")


@_attrs_define
class SmartListFindArgs:
    """PersonFindArgs.

    Attributes:
        allow_archived (bool):
        include_notes (bool):
        include_tags (bool):
        include_items (bool):
        include_item_notes (bool):
        filter_ref_ids (Union[None, Unset, list[str]]):
        filter_is_done (Union[None, Unset, bool]):
        filter_tag_names (Union[None, Unset, list[str]]):
        filter_tag_ref_id (Union[None, Unset, list[str]]):
        filter_item_ref_id (Union[None, Unset, list[str]]):
    """

    allow_archived: bool
    include_notes: bool
    include_tags: bool
    include_items: bool
    include_item_notes: bool
    filter_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_is_done: Union[None, Unset, bool] = UNSET
    filter_tag_names: Union[None, Unset, list[str]] = UNSET
    filter_tag_ref_id: Union[None, Unset, list[str]] = UNSET
    filter_item_ref_id: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        include_tags = self.include_tags

        include_items = self.include_items

        include_item_notes = self.include_item_notes

        filter_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = UNSET
        elif isinstance(self.filter_ref_ids, list):
            filter_ref_ids = self.filter_ref_ids

        else:
            filter_ref_ids = self.filter_ref_ids

        filter_is_done: Union[None, Unset, bool]
        if isinstance(self.filter_is_done, Unset):
            filter_is_done = UNSET
        else:
            filter_is_done = self.filter_is_done

        filter_tag_names: Union[None, Unset, list[str]]
        if isinstance(self.filter_tag_names, Unset):
            filter_tag_names = UNSET
        elif isinstance(self.filter_tag_names, list):
            filter_tag_names = self.filter_tag_names

        else:
            filter_tag_names = self.filter_tag_names

        filter_tag_ref_id: Union[None, Unset, list[str]]
        if isinstance(self.filter_tag_ref_id, Unset):
            filter_tag_ref_id = UNSET
        elif isinstance(self.filter_tag_ref_id, list):
            filter_tag_ref_id = self.filter_tag_ref_id

        else:
            filter_tag_ref_id = self.filter_tag_ref_id

        filter_item_ref_id: Union[None, Unset, list[str]]
        if isinstance(self.filter_item_ref_id, Unset):
            filter_item_ref_id = UNSET
        elif isinstance(self.filter_item_ref_id, list):
            filter_item_ref_id = self.filter_item_ref_id

        else:
            filter_item_ref_id = self.filter_item_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "include_notes": include_notes,
                "include_tags": include_tags,
                "include_items": include_items,
                "include_item_notes": include_item_notes,
            }
        )
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids
        if filter_is_done is not UNSET:
            field_dict["filter_is_done"] = filter_is_done
        if filter_tag_names is not UNSET:
            field_dict["filter_tag_names"] = filter_tag_names
        if filter_tag_ref_id is not UNSET:
            field_dict["filter_tag_ref_id"] = filter_tag_ref_id
        if filter_item_ref_id is not UNSET:
            field_dict["filter_item_ref_id"] = filter_item_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_archived = d.pop("allow_archived")

        include_notes = d.pop("include_notes")

        include_tags = d.pop("include_tags")

        include_items = d.pop("include_items")

        include_item_notes = d.pop("include_item_notes")

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

        def _parse_filter_is_done(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        filter_is_done = _parse_filter_is_done(d.pop("filter_is_done", UNSET))

        def _parse_filter_tag_names(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_tag_names_type_0 = cast(list[str], data)

                return filter_tag_names_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_tag_names = _parse_filter_tag_names(d.pop("filter_tag_names", UNSET))

        def _parse_filter_tag_ref_id(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_tag_ref_id_type_0 = cast(list[str], data)

                return filter_tag_ref_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_tag_ref_id = _parse_filter_tag_ref_id(d.pop("filter_tag_ref_id", UNSET))

        def _parse_filter_item_ref_id(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_item_ref_id_type_0 = cast(list[str], data)

                return filter_item_ref_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_item_ref_id = _parse_filter_item_ref_id(d.pop("filter_item_ref_id", UNSET))

        smart_list_find_args = cls(
            allow_archived=allow_archived,
            include_notes=include_notes,
            include_tags=include_tags,
            include_items=include_items,
            include_item_notes=include_item_notes,
            filter_ref_ids=filter_ref_ids,
            filter_is_done=filter_is_done,
            filter_tag_names=filter_tag_names,
            filter_tag_ref_id=filter_tag_ref_id,
            filter_item_ref_id=filter_item_ref_id,
        )

        smart_list_find_args.additional_properties = d
        return smart_list_find_args

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
