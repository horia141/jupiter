from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.calendar_events_entries import CalendarEventsEntries
    from ..models.calendar_events_stats import CalendarEventsStats


T = TypeVar("T", bound="CalendarLoadForDateAndPeriodResult")


@_attrs_define
class CalendarLoadForDateAndPeriodResult:
    """Result.

    Attributes:
        right_now (str): A date or possibly a datetime for the application.
        period (RecurringTaskPeriod): A period for a particular task.
        period_start_date (str): A date or possibly a datetime for the application.
        period_end_date (str): A date or possibly a datetime for the application.
        prev_period_start_date (str): A date or possibly a datetime for the application.
        next_period_start_date (str): A date or possibly a datetime for the application.
        stats_subperiod (Union[None, RecurringTaskPeriod, Unset]):
        entries (Union['CalendarEventsEntries', None, Unset]):
        stats (Union['CalendarEventsStats', None, Unset]):
    """

    right_now: str
    period: RecurringTaskPeriod
    period_start_date: str
    period_end_date: str
    prev_period_start_date: str
    next_period_start_date: str
    stats_subperiod: Union[None, RecurringTaskPeriod, Unset] = UNSET
    entries: Union["CalendarEventsEntries", None, Unset] = UNSET
    stats: Union["CalendarEventsStats", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.calendar_events_entries import CalendarEventsEntries
        from ..models.calendar_events_stats import CalendarEventsStats

        right_now = self.right_now

        period = self.period.value

        period_start_date = self.period_start_date

        period_end_date = self.period_end_date

        prev_period_start_date = self.prev_period_start_date

        next_period_start_date = self.next_period_start_date

        stats_subperiod: Union[None, Unset, str]
        if isinstance(self.stats_subperiod, Unset):
            stats_subperiod = UNSET
        elif isinstance(self.stats_subperiod, RecurringTaskPeriod):
            stats_subperiod = self.stats_subperiod.value
        else:
            stats_subperiod = self.stats_subperiod

        entries: Union[Dict[str, Any], None, Unset]
        if isinstance(self.entries, Unset):
            entries = UNSET
        elif isinstance(self.entries, CalendarEventsEntries):
            entries = self.entries.to_dict()
        else:
            entries = self.entries

        stats: Union[Dict[str, Any], None, Unset]
        if isinstance(self.stats, Unset):
            stats = UNSET
        elif isinstance(self.stats, CalendarEventsStats):
            stats = self.stats.to_dict()
        else:
            stats = self.stats

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "right_now": right_now,
                "period": period,
                "period_start_date": period_start_date,
                "period_end_date": period_end_date,
                "prev_period_start_date": prev_period_start_date,
                "next_period_start_date": next_period_start_date,
            }
        )
        if stats_subperiod is not UNSET:
            field_dict["stats_subperiod"] = stats_subperiod
        if entries is not UNSET:
            field_dict["entries"] = entries
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.calendar_events_entries import CalendarEventsEntries
        from ..models.calendar_events_stats import CalendarEventsStats

        d = src_dict.copy()
        right_now = d.pop("right_now")

        period = RecurringTaskPeriod(d.pop("period"))

        period_start_date = d.pop("period_start_date")

        period_end_date = d.pop("period_end_date")

        prev_period_start_date = d.pop("prev_period_start_date")

        next_period_start_date = d.pop("next_period_start_date")

        def _parse_stats_subperiod(data: object) -> Union[None, RecurringTaskPeriod, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stats_subperiod_type_0 = RecurringTaskPeriod(data)

                return stats_subperiod_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RecurringTaskPeriod, Unset], data)

        stats_subperiod = _parse_stats_subperiod(d.pop("stats_subperiod", UNSET))

        def _parse_entries(data: object) -> Union["CalendarEventsEntries", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                entries_type_0 = CalendarEventsEntries.from_dict(data)

                return entries_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CalendarEventsEntries", None, Unset], data)

        entries = _parse_entries(d.pop("entries", UNSET))

        def _parse_stats(data: object) -> Union["CalendarEventsStats", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                stats_type_0 = CalendarEventsStats.from_dict(data)

                return stats_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CalendarEventsStats", None, Unset], data)

        stats = _parse_stats(d.pop("stats", UNSET))

        calendar_load_for_date_and_period_result = cls(
            right_now=right_now,
            period=period,
            period_start_date=period_start_date,
            period_end_date=period_end_date,
            prev_period_start_date=prev_period_start_date,
            next_period_start_date=next_period_start_date,
            stats_subperiod=stats_subperiod,
            entries=entries,
            stats=stats,
        )

        calendar_load_for_date_and_period_result.additional_properties = d
        return calendar_load_for_date_and_period_result

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
