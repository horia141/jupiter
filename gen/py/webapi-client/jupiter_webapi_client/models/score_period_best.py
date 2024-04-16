from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScorePeriodBest")


@_attrs_define
class ScorePeriodBest:
    """The best score for a period of time and a particular subdivision of it.

    Attributes:
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        score_log (str):
        timeline (str):
        sub_period (RecurringTaskPeriod): A period for a particular task.
        total_score (int):
        inbox_task_cnt (int):
        big_plan_cnt (int):
        period (Union[Unset, RecurringTaskPeriod]): A period for a particular task.
    """

    created_time: str
    last_modified_time: str
    score_log: str
    timeline: str
    sub_period: RecurringTaskPeriod
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int
    period: Union[Unset, RecurringTaskPeriod] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_time = self.created_time

        last_modified_time = self.last_modified_time

        score_log = self.score_log

        timeline = self.timeline

        sub_period = self.sub_period.value

        total_score = self.total_score

        inbox_task_cnt = self.inbox_task_cnt

        big_plan_cnt = self.big_plan_cnt

        period: Union[Unset, str] = UNSET
        if not isinstance(self.period, Unset):
            period = self.period.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "score_log": score_log,
                "timeline": timeline,
                "sub_period": sub_period,
                "total_score": total_score,
                "inbox_task_cnt": inbox_task_cnt,
                "big_plan_cnt": big_plan_cnt,
            }
        )
        if period is not UNSET:
            field_dict["period"] = period

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        score_log = d.pop("score_log")

        timeline = d.pop("timeline")

        sub_period = RecurringTaskPeriod(d.pop("sub_period"))

        total_score = d.pop("total_score")

        inbox_task_cnt = d.pop("inbox_task_cnt")

        big_plan_cnt = d.pop("big_plan_cnt")

        _period = d.pop("period", UNSET)
        period: Union[Unset, RecurringTaskPeriod]
        if isinstance(_period, Unset):
            period = UNSET
        else:
            period = RecurringTaskPeriod(_period)

        score_period_best = cls(
            created_time=created_time,
            last_modified_time=last_modified_time,
            score_log=score_log,
            timeline=timeline,
            sub_period=sub_period,
            total_score=total_score,
            inbox_task_cnt=inbox_task_cnt,
            big_plan_cnt=big_plan_cnt,
            period=period,
        )

        score_period_best.additional_properties = d
        return score_period_best

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
