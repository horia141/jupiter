from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_score_overview import UserScoreOverview


T = TypeVar("T", bound="RecordScoreResult")


@_attrs_define
class RecordScoreResult:
    """The result of the score recording.

    Attributes:
        latest_task_score (int):
        score_overview (UserScoreOverview): An overview of the scores for a user.
        has_lucky_puppy_bonus (Union[None, Unset, bool]):
    """

    latest_task_score: int
    score_overview: "UserScoreOverview"
    has_lucky_puppy_bonus: Union[None, Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        latest_task_score = self.latest_task_score

        score_overview = self.score_overview.to_dict()

        has_lucky_puppy_bonus: Union[None, Unset, bool]
        if isinstance(self.has_lucky_puppy_bonus, Unset):
            has_lucky_puppy_bonus = UNSET
        else:
            has_lucky_puppy_bonus = self.has_lucky_puppy_bonus

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "latest_task_score": latest_task_score,
                "score_overview": score_overview,
            }
        )
        if has_lucky_puppy_bonus is not UNSET:
            field_dict["has_lucky_puppy_bonus"] = has_lucky_puppy_bonus

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_score_overview import UserScoreOverview

        d = src_dict.copy()
        latest_task_score = d.pop("latest_task_score")

        score_overview = UserScoreOverview.from_dict(d.pop("score_overview"))

        def _parse_has_lucky_puppy_bonus(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        has_lucky_puppy_bonus = _parse_has_lucky_puppy_bonus(d.pop("has_lucky_puppy_bonus", UNSET))

        record_score_result = cls(
            latest_task_score=latest_task_score,
            score_overview=score_overview,
            has_lucky_puppy_bonus=has_lucky_puppy_bonus,
        )

        record_score_result.additional_properties = d
        return record_score_result

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
