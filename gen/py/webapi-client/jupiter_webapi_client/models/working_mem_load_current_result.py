from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.working_mem_load_current_entry import WorkingMemLoadCurrentEntry


T = TypeVar("T", bound="WorkingMemLoadCurrentResult")


@_attrs_define
class WorkingMemLoadCurrentResult:
    """Working mem load current result.

    Attributes:
        entry (Union[Unset, WorkingMemLoadCurrentEntry]): Working mem load current entry.
    """

    entry: Union[Unset, "WorkingMemLoadCurrentEntry"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        entry: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.entry, Unset):
            entry = self.entry.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry is not UNSET:
            field_dict["entry"] = entry

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.working_mem_load_current_entry import WorkingMemLoadCurrentEntry

        d = src_dict.copy()
        _entry = d.pop("entry", UNSET)
        entry: Union[Unset, WorkingMemLoadCurrentEntry]
        if isinstance(_entry, Unset):
            entry = UNSET
        else:
            entry = WorkingMemLoadCurrentEntry.from_dict(_entry)

        working_mem_load_current_result = cls(
            entry=entry,
        )

        working_mem_load_current_result.additional_properties = d
        return working_mem_load_current_result

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
