from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_task_entry import InboxTaskEntry
    from ..models.person_entry import PersonEntry
    from ..models.schedule_full_days_event_entry import ScheduleFullDaysEventEntry
    from ..models.schedule_in_day_event_entry import ScheduleInDayEventEntry
    from ..models.vacation_entry import VacationEntry


T = TypeVar("T", bound="CalendarEventsEntries")


@_attrs_define
class CalendarEventsEntries:
    """Full entries for results.

    Attributes:
        schedule_event_full_days_entries (List['ScheduleFullDaysEventEntry']):
        schedule_event_in_day_entries (List['ScheduleInDayEventEntry']):
        inbox_task_entries (List['InboxTaskEntry']):
        person_entries (List['PersonEntry']):
        vacation_entries (List['VacationEntry']):
    """

    schedule_event_full_days_entries: List["ScheduleFullDaysEventEntry"]
    schedule_event_in_day_entries: List["ScheduleInDayEventEntry"]
    inbox_task_entries: List["InboxTaskEntry"]
    person_entries: List["PersonEntry"]
    vacation_entries: List["VacationEntry"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        schedule_event_full_days_entries = []
        for schedule_event_full_days_entries_item_data in self.schedule_event_full_days_entries:
            schedule_event_full_days_entries_item = schedule_event_full_days_entries_item_data.to_dict()
            schedule_event_full_days_entries.append(schedule_event_full_days_entries_item)

        schedule_event_in_day_entries = []
        for schedule_event_in_day_entries_item_data in self.schedule_event_in_day_entries:
            schedule_event_in_day_entries_item = schedule_event_in_day_entries_item_data.to_dict()
            schedule_event_in_day_entries.append(schedule_event_in_day_entries_item)

        inbox_task_entries = []
        for inbox_task_entries_item_data in self.inbox_task_entries:
            inbox_task_entries_item = inbox_task_entries_item_data.to_dict()
            inbox_task_entries.append(inbox_task_entries_item)

        person_entries = []
        for person_entries_item_data in self.person_entries:
            person_entries_item = person_entries_item_data.to_dict()
            person_entries.append(person_entries_item)

        vacation_entries = []
        for vacation_entries_item_data in self.vacation_entries:
            vacation_entries_item = vacation_entries_item_data.to_dict()
            vacation_entries.append(vacation_entries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schedule_event_full_days_entries": schedule_event_full_days_entries,
                "schedule_event_in_day_entries": schedule_event_in_day_entries,
                "inbox_task_entries": inbox_task_entries,
                "person_entries": person_entries,
                "vacation_entries": vacation_entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task_entry import InboxTaskEntry
        from ..models.person_entry import PersonEntry
        from ..models.schedule_full_days_event_entry import ScheduleFullDaysEventEntry
        from ..models.schedule_in_day_event_entry import ScheduleInDayEventEntry
        from ..models.vacation_entry import VacationEntry

        d = src_dict.copy()
        schedule_event_full_days_entries = []
        _schedule_event_full_days_entries = d.pop("schedule_event_full_days_entries")
        for schedule_event_full_days_entries_item_data in _schedule_event_full_days_entries:
            schedule_event_full_days_entries_item = ScheduleFullDaysEventEntry.from_dict(
                schedule_event_full_days_entries_item_data
            )

            schedule_event_full_days_entries.append(schedule_event_full_days_entries_item)

        schedule_event_in_day_entries = []
        _schedule_event_in_day_entries = d.pop("schedule_event_in_day_entries")
        for schedule_event_in_day_entries_item_data in _schedule_event_in_day_entries:
            schedule_event_in_day_entries_item = ScheduleInDayEventEntry.from_dict(
                schedule_event_in_day_entries_item_data
            )

            schedule_event_in_day_entries.append(schedule_event_in_day_entries_item)

        inbox_task_entries = []
        _inbox_task_entries = d.pop("inbox_task_entries")
        for inbox_task_entries_item_data in _inbox_task_entries:
            inbox_task_entries_item = InboxTaskEntry.from_dict(inbox_task_entries_item_data)

            inbox_task_entries.append(inbox_task_entries_item)

        person_entries = []
        _person_entries = d.pop("person_entries")
        for person_entries_item_data in _person_entries:
            person_entries_item = PersonEntry.from_dict(person_entries_item_data)

            person_entries.append(person_entries_item)

        vacation_entries = []
        _vacation_entries = d.pop("vacation_entries")
        for vacation_entries_item_data in _vacation_entries:
            vacation_entries_item = VacationEntry.from_dict(vacation_entries_item_data)

            vacation_entries.append(vacation_entries_item)

        calendar_events_entries = cls(
            schedule_event_full_days_entries=schedule_event_full_days_entries,
            schedule_event_in_day_entries=schedule_event_in_day_entries,
            inbox_task_entries=inbox_task_entries,
            person_entries=person_entries,
            vacation_entries=vacation_entries,
        )

        calendar_events_entries.additional_properties = d
        return calendar_events_entries

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
