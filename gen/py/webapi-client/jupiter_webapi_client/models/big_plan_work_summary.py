from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BigPlanWorkSummary")


@_attrs_define
class BigPlanWorkSummary:
    """The report for a big plan.

    Attributes:
        created_cnt (int):
        not_started_cnt (int):
        working_cnt (int):
        not_done_cnt (int):
        not_done_ratio (float):
        done_cnt (int):
        done_ratio (float):
    """

    created_cnt: int
    not_started_cnt: int
    working_cnt: int
    not_done_cnt: int
    not_done_ratio: float
    done_cnt: int
    done_ratio: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_cnt = self.created_cnt

        not_started_cnt = self.not_started_cnt

        working_cnt = self.working_cnt

        not_done_cnt = self.not_done_cnt

        not_done_ratio = self.not_done_ratio

        done_cnt = self.done_cnt

        done_ratio = self.done_ratio

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_cnt": created_cnt,
                "not_started_cnt": not_started_cnt,
                "working_cnt": working_cnt,
                "not_done_cnt": not_done_cnt,
                "not_done_ratio": not_done_ratio,
                "done_cnt": done_cnt,
                "done_ratio": done_ratio,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_cnt = d.pop("created_cnt")

        not_started_cnt = d.pop("not_started_cnt")

        working_cnt = d.pop("working_cnt")

        not_done_cnt = d.pop("not_done_cnt")

        not_done_ratio = d.pop("not_done_ratio")

        done_cnt = d.pop("done_cnt")

        done_ratio = d.pop("done_ratio")

        big_plan_work_summary = cls(
            created_cnt=created_cnt,
            not_started_cnt=not_started_cnt,
            working_cnt=working_cnt,
            not_done_cnt=not_done_cnt,
            not_done_ratio=not_done_ratio,
            done_cnt=done_cnt,
            done_ratio=done_ratio,
        )

        big_plan_work_summary.additional_properties = d
        return big_plan_work_summary

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
