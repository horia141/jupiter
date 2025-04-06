from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.inbox_task_status import InboxTaskStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailTaskUpdateArgsGenerationStatus")


@_attrs_define
class EmailTaskUpdateArgsGenerationStatus:
    """
    Attributes:
        should_change (bool):
        value (Union[InboxTaskStatus, None, Unset]):
    """

    should_change: bool
    value: Union[InboxTaskStatus, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        should_change = self.should_change

        value: Union[None, Unset, str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, InboxTaskStatus):
            value = self.value.value
        else:
            value = self.value

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
        d = dict(src_dict)
        should_change = d.pop("should_change")

        def _parse_value(data: object) -> Union[InboxTaskStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                value_type_0 = InboxTaskStatus(data)

                return value_type_0
            except:  # noqa: E722
                pass
            return cast(Union[InboxTaskStatus, None, Unset], data)

        value = _parse_value(d.pop("value", UNSET))

        email_task_update_args_generation_status = cls(
            should_change=should_change,
            value=value,
        )

        email_task_update_args_generation_status.additional_properties = d
        return email_task_update_args_generation_status

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
