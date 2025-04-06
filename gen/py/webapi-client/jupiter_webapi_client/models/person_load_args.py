from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonLoadArgs")


@_attrs_define
class PersonLoadArgs:
    """PersonLoadArgs.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
        catch_up_task_retrieve_offset (Union[None, Unset, int]):
        birthday_task_retrieve_offset (Union[None, Unset, int]):
    """

    ref_id: str
    allow_archived: bool
    catch_up_task_retrieve_offset: Union[None, Unset, int] = UNSET
    birthday_task_retrieve_offset: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        catch_up_task_retrieve_offset: Union[None, Unset, int]
        if isinstance(self.catch_up_task_retrieve_offset, Unset):
            catch_up_task_retrieve_offset = UNSET
        else:
            catch_up_task_retrieve_offset = self.catch_up_task_retrieve_offset

        birthday_task_retrieve_offset: Union[None, Unset, int]
        if isinstance(self.birthday_task_retrieve_offset, Unset):
            birthday_task_retrieve_offset = UNSET
        else:
            birthday_task_retrieve_offset = self.birthday_task_retrieve_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
            }
        )
        if catch_up_task_retrieve_offset is not UNSET:
            field_dict["catch_up_task_retrieve_offset"] = catch_up_task_retrieve_offset
        if birthday_task_retrieve_offset is not UNSET:
            field_dict["birthday_task_retrieve_offset"] = birthday_task_retrieve_offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        def _parse_catch_up_task_retrieve_offset(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        catch_up_task_retrieve_offset = _parse_catch_up_task_retrieve_offset(
            d.pop("catch_up_task_retrieve_offset", UNSET)
        )

        def _parse_birthday_task_retrieve_offset(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        birthday_task_retrieve_offset = _parse_birthday_task_retrieve_offset(
            d.pop("birthday_task_retrieve_offset", UNSET)
        )

        person_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
            catch_up_task_retrieve_offset=catch_up_task_retrieve_offset,
            birthday_task_retrieve_offset=birthday_task_retrieve_offset,
        )

        person_load_args.additional_properties = d
        return person_load_args

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
