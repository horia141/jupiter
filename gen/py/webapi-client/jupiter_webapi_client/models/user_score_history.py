from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_score_at_date import UserScoreAtDate


T = TypeVar("T", bound="UserScoreHistory")


@_attrs_define
class UserScoreHistory:
    """A history of user scores over time.

    Attributes:
        daily_scores (List['UserScoreAtDate']):
        weekly_scores (List['UserScoreAtDate']):
        monthly_scores (List['UserScoreAtDate']):
        quarterly_scores (List['UserScoreAtDate']):
    """

    daily_scores: List["UserScoreAtDate"]
    weekly_scores: List["UserScoreAtDate"]
    monthly_scores: List["UserScoreAtDate"]
    quarterly_scores: List["UserScoreAtDate"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        daily_scores = []
        for daily_scores_item_data in self.daily_scores:
            daily_scores_item = daily_scores_item_data.to_dict()
            daily_scores.append(daily_scores_item)

        weekly_scores = []
        for weekly_scores_item_data in self.weekly_scores:
            weekly_scores_item = weekly_scores_item_data.to_dict()
            weekly_scores.append(weekly_scores_item)

        monthly_scores = []
        for monthly_scores_item_data in self.monthly_scores:
            monthly_scores_item = monthly_scores_item_data.to_dict()
            monthly_scores.append(monthly_scores_item)

        quarterly_scores = []
        for quarterly_scores_item_data in self.quarterly_scores:
            quarterly_scores_item = quarterly_scores_item_data.to_dict()
            quarterly_scores.append(quarterly_scores_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "daily_scores": daily_scores,
                "weekly_scores": weekly_scores,
                "monthly_scores": monthly_scores,
                "quarterly_scores": quarterly_scores,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_score_at_date import UserScoreAtDate

        d = src_dict.copy()
        daily_scores = []
        _daily_scores = d.pop("daily_scores")
        for daily_scores_item_data in _daily_scores:
            daily_scores_item = UserScoreAtDate.from_dict(daily_scores_item_data)

            daily_scores.append(daily_scores_item)

        weekly_scores = []
        _weekly_scores = d.pop("weekly_scores")
        for weekly_scores_item_data in _weekly_scores:
            weekly_scores_item = UserScoreAtDate.from_dict(weekly_scores_item_data)

            weekly_scores.append(weekly_scores_item)

        monthly_scores = []
        _monthly_scores = d.pop("monthly_scores")
        for monthly_scores_item_data in _monthly_scores:
            monthly_scores_item = UserScoreAtDate.from_dict(monthly_scores_item_data)

            monthly_scores.append(monthly_scores_item)

        quarterly_scores = []
        _quarterly_scores = d.pop("quarterly_scores")
        for quarterly_scores_item_data in _quarterly_scores:
            quarterly_scores_item = UserScoreAtDate.from_dict(quarterly_scores_item_data)

            quarterly_scores.append(quarterly_scores_item)

        user_score_history = cls(
            daily_scores=daily_scores,
            weekly_scores=weekly_scores,
            monthly_scores=monthly_scores,
            quarterly_scores=quarterly_scores,
        )

        user_score_history.additional_properties = d
        return user_score_history

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
