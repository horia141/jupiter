from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.journal_update_settings_args_generation_in_advance_days_value import (
        JournalUpdateSettingsArgsGenerationInAdvanceDaysValue,
    )


T = TypeVar("T", bound="JournalUpdateSettingsArgsGenerationInAdvanceDays")


@_attrs_define
class JournalUpdateSettingsArgsGenerationInAdvanceDays:
    """
    Attributes:
        should_change (bool):
        value (Union[Unset, JournalUpdateSettingsArgsGenerationInAdvanceDaysValue]):
    """

    should_change: bool
    value: Union[Unset, "JournalUpdateSettingsArgsGenerationInAdvanceDaysValue"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        should_change = self.should_change

        value: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "should_change": should_change,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal_update_settings_args_generation_in_advance_days_value import (
            JournalUpdateSettingsArgsGenerationInAdvanceDaysValue,
        )

        d = dict(src_dict)
        should_change = d.pop("should_change")

        _value = d.pop("value", UNSET)
        value: Union[Unset, JournalUpdateSettingsArgsGenerationInAdvanceDaysValue]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = JournalUpdateSettingsArgsGenerationInAdvanceDaysValue.from_dict(_value)

        journal_update_settings_args_generation_in_advance_days = cls(
            should_change=should_change,
            value=value,
        )

        journal_update_settings_args_generation_in_advance_days.additional_properties = d
        return journal_update_settings_args_generation_in_advance_days

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
