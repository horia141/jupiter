from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

T = TypeVar("T", bound="JournalLoadForDateAndPeriodArgs")


@_attrs_define
class JournalLoadForDateAndPeriodArgs:
    """Args.

    Attributes:
        right_now (str): A date or possibly a datetime for the application.
        period (RecurringTaskPeriod): A period for a particular task.
        allow_archived (bool):
    """

    right_now: str
    period: RecurringTaskPeriod
    allow_archived: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        right_now = self.right_now

        period = self.period.value

        allow_archived = self.allow_archived

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "right_now": right_now,
                "period": period,
                "allow_archived": allow_archived,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        right_now = d.pop("right_now")

        period = RecurringTaskPeriod(d.pop("period"))

        allow_archived = d.pop("allow_archived")

        journal_load_for_date_and_period_args = cls(
            right_now=right_now,
            period=period,
            allow_archived=allow_archived,
        )

        journal_load_for_date_and_period_args.additional_properties = d
        return journal_load_for_date_and_period_args

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
