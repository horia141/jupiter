from typing import Any, Dict, List, Type, TypeVar, Union, cast

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
        filter_ref_ids (Union[Unset, List[str]]):
        filter_is_done (Union[Unset, bool]):
        filter_tag_names (Union[Unset, List[str]]):
        filter_tag_ref_id (Union[Unset, List[str]]):
        filter_item_ref_id (Union[Unset, List[str]]):
    """

    allow_archived: bool
    include_notes: bool
    include_tags: bool
    include_items: bool
    include_item_notes: bool
    filter_ref_ids: Union[Unset, List[str]] = UNSET
    filter_is_done: Union[Unset, bool] = UNSET
    filter_tag_names: Union[Unset, List[str]] = UNSET
    filter_tag_ref_id: Union[Unset, List[str]] = UNSET
    filter_item_ref_id: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_notes = self.include_notes

        include_tags = self.include_tags

        include_items = self.include_items

        include_item_notes = self.include_item_notes

        filter_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = self.filter_ref_ids

        filter_is_done = self.filter_is_done

        filter_tag_names: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_tag_names, Unset):
            filter_tag_names = self.filter_tag_names

        filter_tag_ref_id: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_tag_ref_id, Unset):
            filter_tag_ref_id = self.filter_tag_ref_id

        filter_item_ref_id: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_item_ref_id, Unset):
            filter_item_ref_id = self.filter_item_ref_id

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        include_notes = d.pop("include_notes")

        include_tags = d.pop("include_tags")

        include_items = d.pop("include_items")

        include_item_notes = d.pop("include_item_notes")

        filter_ref_ids = cast(List[str], d.pop("filter_ref_ids", UNSET))

        filter_is_done = d.pop("filter_is_done", UNSET)

        filter_tag_names = cast(List[str], d.pop("filter_tag_names", UNSET))

        filter_tag_ref_id = cast(List[str], d.pop("filter_tag_ref_id", UNSET))

        filter_item_ref_id = cast(List[str], d.pop("filter_item_ref_id", UNSET))

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
