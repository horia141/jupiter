from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

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
        entry (Union['WorkingMemLoadCurrentEntry', None, Unset]):
    """

    entry: Union["WorkingMemLoadCurrentEntry", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.working_mem_load_current_entry import WorkingMemLoadCurrentEntry

        entry: Union[None, Unset, dict[str, Any]]
        if isinstance(self.entry, Unset):
            entry = UNSET
        elif isinstance(self.entry, WorkingMemLoadCurrentEntry):
            entry = self.entry.to_dict()
        else:
            entry = self.entry

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry is not UNSET:
            field_dict["entry"] = entry

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.working_mem_load_current_entry import WorkingMemLoadCurrentEntry

        d = dict(src_dict)

        def _parse_entry(data: object) -> Union["WorkingMemLoadCurrentEntry", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                entry_type_0 = WorkingMemLoadCurrentEntry.from_dict(data)

                return entry_type_0
            except:  # noqa: E722
                pass
            return cast(Union["WorkingMemLoadCurrentEntry", None, Unset], data)

        entry = _parse_entry(d.pop("entry", UNSET))

        working_mem_load_current_result = cls(
            entry=entry,
        )

        working_mem_load_current_result.additional_properties = d
        return working_mem_load_current_result

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
