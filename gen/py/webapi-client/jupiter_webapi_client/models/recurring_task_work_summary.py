from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RecurringTaskWorkSummary")


@_attrs_define
class RecurringTaskWorkSummary:
    """The reporting summary.

    Attributes:
        created_cnt (int):
        accepted_cnt (int):
        working_cnt (int):
        not_done_cnt (int):
        not_done_ratio (float):
        done_cnt (int):
        done_ratio (float):
        streak_plot (str):
    """

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    not_done_ratio: float
    done_cnt: int
    done_ratio: float
    streak_plot: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_cnt = self.created_cnt

        accepted_cnt = self.accepted_cnt

        working_cnt = self.working_cnt

        not_done_cnt = self.not_done_cnt

        not_done_ratio = self.not_done_ratio

        done_cnt = self.done_cnt

        done_ratio = self.done_ratio

        streak_plot = self.streak_plot

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_cnt": created_cnt,
                "accepted_cnt": accepted_cnt,
                "working_cnt": working_cnt,
                "not_done_cnt": not_done_cnt,
                "not_done_ratio": not_done_ratio,
                "done_cnt": done_cnt,
                "done_ratio": done_ratio,
                "streak_plot": streak_plot,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_cnt = d.pop("created_cnt")

        accepted_cnt = d.pop("accepted_cnt")

        working_cnt = d.pop("working_cnt")

        not_done_cnt = d.pop("not_done_cnt")

        not_done_ratio = d.pop("not_done_ratio")

        done_cnt = d.pop("done_cnt")

        done_ratio = d.pop("done_ratio")

        streak_plot = d.pop("streak_plot")

        recurring_task_work_summary = cls(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            not_done_cnt=not_done_cnt,
            not_done_ratio=not_done_ratio,
            done_cnt=done_cnt,
            done_ratio=done_ratio,
            streak_plot=streak_plot,
        )

        recurring_task_work_summary.additional_properties = d
        return recurring_task_work_summary

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
