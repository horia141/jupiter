from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="CalendarLoadForDateAndPeriodArgs")


@_attrs_define
class CalendarLoadForDateAndPeriodArgs:
    """Args.

    Attributes:
        right_now (str): A date or possibly a datetime for the application.
        period (RecurringTaskPeriod): A period for a particular task.
        stats_subperiod (Union[None, RecurringTaskPeriod, Unset]):
    """

    right_now: str
    period: RecurringTaskPeriod
    stats_subperiod: Union[None, RecurringTaskPeriod, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        right_now = self.right_now

        period = self.period.value

        stats_subperiod: Union[None, Unset, str]
        if isinstance(self.stats_subperiod, Unset):
            stats_subperiod = UNSET
        elif isinstance(self.stats_subperiod, RecurringTaskPeriod):
            stats_subperiod = self.stats_subperiod.value
        else:
            stats_subperiod = self.stats_subperiod

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "right_now": right_now,
                "period": period,
            }
        )
        if stats_subperiod is not UNSET:
            field_dict["stats_subperiod"] = stats_subperiod

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        right_now = d.pop("right_now")

        period = RecurringTaskPeriod(d.pop("period"))

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

        calendar_load_for_date_and_period_args = cls(
            right_now=right_now,
            period=period,
            stats_subperiod=stats_subperiod,
        )

        calendar_load_for_date_and_period_args.additional_properties = d
        return calendar_load_for_date_and_period_args

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
