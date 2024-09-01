from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

T = TypeVar("T", bound="CalendarEventsStatsPerSubperiod")


@_attrs_define
class CalendarEventsStatsPerSubperiod:
    """Stats about a particular subperiod.

    Attributes:
        period (RecurringTaskPeriod): A period for a particular task.
        period_start_date (str): A date or possibly a datetime for the application.
        schedule_event_full_days_cnt (int):
        schedule_event_in_day_cnt (int):
        inbox_task_cnt (int):
        person_birthday_cnt (int):
    """

    period: RecurringTaskPeriod
    period_start_date: str
    schedule_event_full_days_cnt: int
    schedule_event_in_day_cnt: int
    inbox_task_cnt: int
    person_birthday_cnt: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        period = self.period.value

        period_start_date = self.period_start_date

        schedule_event_full_days_cnt = self.schedule_event_full_days_cnt

        schedule_event_in_day_cnt = self.schedule_event_in_day_cnt

        inbox_task_cnt = self.inbox_task_cnt

        person_birthday_cnt = self.person_birthday_cnt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "period_start_date": period_start_date,
                "schedule_event_full_days_cnt": schedule_event_full_days_cnt,
                "schedule_event_in_day_cnt": schedule_event_in_day_cnt,
                "inbox_task_cnt": inbox_task_cnt,
                "person_birthday_cnt": person_birthday_cnt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        period = RecurringTaskPeriod(d.pop("period"))

        period_start_date = d.pop("period_start_date")

        schedule_event_full_days_cnt = d.pop("schedule_event_full_days_cnt")

        schedule_event_in_day_cnt = d.pop("schedule_event_in_day_cnt")

        inbox_task_cnt = d.pop("inbox_task_cnt")

        person_birthday_cnt = d.pop("person_birthday_cnt")

        calendar_events_stats_per_subperiod = cls(
            period=period,
            period_start_date=period_start_date,
            schedule_event_full_days_cnt=schedule_event_full_days_cnt,
            schedule_event_in_day_cnt=schedule_event_in_day_cnt,
            inbox_task_cnt=inbox_task_cnt,
            person_birthday_cnt=person_birthday_cnt,
        )

        calendar_events_stats_per_subperiod.additional_properties = d
        return calendar_events_stats_per_subperiod

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
