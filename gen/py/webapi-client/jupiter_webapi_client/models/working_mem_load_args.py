from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkingMemLoadArgs")


@_attrs_define
class WorkingMemLoadArgs:
    """Working mem find args.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
        cleanup_task_retrieve_offset (Union[None, Unset, int]):
    """

    ref_id: str
    allow_archived: bool
    cleanup_task_retrieve_offset: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        cleanup_task_retrieve_offset: Union[None, Unset, int]
        if isinstance(self.cleanup_task_retrieve_offset, Unset):
            cleanup_task_retrieve_offset = UNSET
        else:
            cleanup_task_retrieve_offset = self.cleanup_task_retrieve_offset

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
            }
        )
        if cleanup_task_retrieve_offset is not UNSET:
            field_dict["cleanup_task_retrieve_offset"] = cleanup_task_retrieve_offset

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        def _parse_cleanup_task_retrieve_offset(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cleanup_task_retrieve_offset = _parse_cleanup_task_retrieve_offset(d.pop("cleanup_task_retrieve_offset", UNSET))

        working_mem_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
            cleanup_task_retrieve_offset=cleanup_task_retrieve_offset,
        )

        working_mem_load_args.additional_properties = d
        return working_mem_load_args

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
