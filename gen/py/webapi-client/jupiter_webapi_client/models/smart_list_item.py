from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SmartListItem")


@_attrs_define
class SmartListItem:
    """A smart list item.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The smart list item name.
        smart_list (str):
        is_done (bool):
        tags_ref_id (List[str]):
        archived_time (Union[Unset, str]): A timestamp in the application.
        url (Union[Unset, str]): A URL in this domain.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    smart_list: str
    is_done: bool
    tags_ref_id: List[str]
    archived_time: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        smart_list = self.smart_list

        is_done = self.is_done

        tags_ref_id = self.tags_ref_id

        archived_time = self.archived_time

        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "smart_list": smart_list,
                "is_done": is_done,
                "tags_ref_id": tags_ref_id,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        smart_list = d.pop("smart_list")

        is_done = d.pop("is_done")

        tags_ref_id = cast(List[str], d.pop("tags_ref_id"))

        archived_time = d.pop("archived_time", UNSET)

        url = d.pop("url", UNSET)

        smart_list_item = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            smart_list=smart_list,
            is_done=is_done,
            tags_ref_id=tags_ref_id,
            archived_time=archived_time,
            url=url,
        )

        smart_list_item.additional_properties = d
        return smart_list_item

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
