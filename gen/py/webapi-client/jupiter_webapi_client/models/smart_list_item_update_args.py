from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_item_update_args_is_done import SmartListItemUpdateArgsIsDone
    from ..models.smart_list_item_update_args_name import SmartListItemUpdateArgsName
    from ..models.smart_list_item_update_args_tags import SmartListItemUpdateArgsTags
    from ..models.smart_list_item_update_args_url import SmartListItemUpdateArgsUrl


T = TypeVar("T", bound="SmartListItemUpdateArgs")


@_attrs_define
class SmartListItemUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (SmartListItemUpdateArgsName):
        is_done (SmartListItemUpdateArgsIsDone):
        tags (SmartListItemUpdateArgsTags):
        url (SmartListItemUpdateArgsUrl):
    """

    ref_id: str
    name: "SmartListItemUpdateArgsName"
    is_done: "SmartListItemUpdateArgsIsDone"
    tags: "SmartListItemUpdateArgsTags"
    url: "SmartListItemUpdateArgsUrl"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        is_done = self.is_done.to_dict()

        tags = self.tags.to_dict()

        url = self.url.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "is_done": is_done,
                "tags": tags,
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.smart_list_item_update_args_is_done import SmartListItemUpdateArgsIsDone
        from ..models.smart_list_item_update_args_name import SmartListItemUpdateArgsName
        from ..models.smart_list_item_update_args_tags import SmartListItemUpdateArgsTags
        from ..models.smart_list_item_update_args_url import SmartListItemUpdateArgsUrl

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = SmartListItemUpdateArgsName.from_dict(d.pop("name"))

        is_done = SmartListItemUpdateArgsIsDone.from_dict(d.pop("is_done"))

        tags = SmartListItemUpdateArgsTags.from_dict(d.pop("tags"))

        url = SmartListItemUpdateArgsUrl.from_dict(d.pop("url"))

        smart_list_item_update_args = cls(
            ref_id=ref_id,
            name=name,
            is_done=is_done,
            tags=tags,
            url=url,
        )

        smart_list_item_update_args.additional_properties = d
        return smart_list_item_update_args

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
