from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SmartListItemCreateArgs")


@_attrs_define
class SmartListItemCreateArgs:
    """SmartListItemCreate args.

    Attributes:
        smart_list_ref_id (str): A generic entity id.
        name (str): The smart list item name.
        is_done (bool):
        tag_names (list[str]):
        url (Union[None, Unset, str]):
    """

    smart_list_ref_id: str
    name: str
    is_done: bool
    tag_names: list[str]
    url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        smart_list_ref_id = self.smart_list_ref_id

        name = self.name

        is_done = self.is_done

        tag_names = self.tag_names

        url: Union[None, Unset, str]
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "smart_list_ref_id": smart_list_ref_id,
                "name": name,
                "is_done": is_done,
                "tag_names": tag_names,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        smart_list_ref_id = d.pop("smart_list_ref_id")

        name = d.pop("name")

        is_done = d.pop("is_done")

        tag_names = cast(list[str], d.pop("tag_names"))

        def _parse_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        url = _parse_url(d.pop("url", UNSET))

        smart_list_item_create_args = cls(
            smart_list_ref_id=smart_list_ref_id,
            name=name,
            is_done=is_done,
            tag_names=tag_names,
            url=url,
        )

        smart_list_item_create_args.additional_properties = d
        return smart_list_item_create_args

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
