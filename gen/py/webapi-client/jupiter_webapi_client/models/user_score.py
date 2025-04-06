from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserScore")


@_attrs_define
class UserScore:
    """A full view of the score for a user.

    Attributes:
        total_score (int):
        inbox_task_cnt (int):
        big_plan_cnt (int):
    """

    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_score = self.total_score

        inbox_task_cnt = self.inbox_task_cnt

        big_plan_cnt = self.big_plan_cnt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_score": total_score,
                "inbox_task_cnt": inbox_task_cnt,
                "big_plan_cnt": big_plan_cnt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_score = d.pop("total_score")

        inbox_task_cnt = d.pop("inbox_task_cnt")

        big_plan_cnt = d.pop("big_plan_cnt")

        user_score = cls(
            total_score=total_score,
            inbox_task_cnt=inbox_task_cnt,
            big_plan_cnt=big_plan_cnt,
        )

        user_score.additional_properties = d
        return user_score

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
