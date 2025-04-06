from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScoreStats")


@_attrs_define
class ScoreStats:
    """Statistics about scores for a particular time interval.

    Attributes:
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        score_log_ref_id (str):
        timeline (str):
        total_score (int):
        inbox_task_cnt (int):
        big_plan_cnt (int):
        period (Union[None, RecurringTaskPeriod, Unset]):
    """

    created_time: str
    last_modified_time: str
    score_log_ref_id: str
    timeline: str
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int
    period: Union[None, RecurringTaskPeriod, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_time = self.created_time

        last_modified_time = self.last_modified_time

        score_log_ref_id = self.score_log_ref_id

        timeline = self.timeline

        total_score = self.total_score

        inbox_task_cnt = self.inbox_task_cnt

        big_plan_cnt = self.big_plan_cnt

        period: Union[None, Unset, str]
        if isinstance(self.period, Unset):
            period = UNSET
        elif isinstance(self.period, RecurringTaskPeriod):
            period = self.period.value
        else:
            period = self.period

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "score_log_ref_id": score_log_ref_id,
                "timeline": timeline,
                "total_score": total_score,
                "inbox_task_cnt": inbox_task_cnt,
                "big_plan_cnt": big_plan_cnt,
            }
        )
        if period is not UNSET:
            field_dict["period"] = period

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        score_log_ref_id = d.pop("score_log_ref_id")

        timeline = d.pop("timeline")

        total_score = d.pop("total_score")

        inbox_task_cnt = d.pop("inbox_task_cnt")

        big_plan_cnt = d.pop("big_plan_cnt")

        def _parse_period(data: object) -> Union[None, RecurringTaskPeriod, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                period_type_0 = RecurringTaskPeriod(data)

                return period_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RecurringTaskPeriod, Unset], data)

        period = _parse_period(d.pop("period", UNSET))

        score_stats = cls(
            created_time=created_time,
            last_modified_time=last_modified_time,
            score_log_ref_id=score_log_ref_id,
            timeline=timeline,
            total_score=total_score,
            inbox_task_cnt=inbox_task_cnt,
            big_plan_cnt=big_plan_cnt,
            period=period,
        )

        score_stats.additional_properties = d
        return score_stats

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
