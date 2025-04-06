from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

T = TypeVar("T", bound="JournalChangePeriodsArgs")


@_attrs_define
class JournalChangePeriodsArgs:
    """Args.

    Attributes:
        periods (list[RecurringTaskPeriod]):
    """

    periods: list[RecurringTaskPeriod]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        periods = []
        for periods_item_data in self.periods:
            periods_item = periods_item_data.value
            periods.append(periods_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        periods = []
        _periods = d.pop("periods")
        for periods_item_data in _periods:
            periods_item = RecurringTaskPeriod(periods_item_data)

            periods.append(periods_item)

        journal_change_periods_args = cls(
            periods=periods,
        )

        journal_change_periods_args.additional_properties = d
        return journal_change_periods_args

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
