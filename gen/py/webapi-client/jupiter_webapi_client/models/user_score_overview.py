from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_score import UserScore


T = TypeVar("T", bound="UserScoreOverview")


@_attrs_define
class UserScoreOverview:
    """An overview of the scores for a user.

    Attributes:
        daily_score (UserScore): A full view of the score for a user.
        weekly_score (UserScore): A full view of the score for a user.
        monthly_score (UserScore): A full view of the score for a user.
        quarterly_score (UserScore): A full view of the score for a user.
        yearly_score (UserScore): A full view of the score for a user.
        lifetime_score (UserScore): A full view of the score for a user.
        best_quarterly_daily_score (UserScore): A full view of the score for a user.
        best_quarterly_weekly_score (UserScore): A full view of the score for a user.
        best_quarterly_monthly_score (UserScore): A full view of the score for a user.
        best_yearly_daily_score (UserScore): A full view of the score for a user.
        best_yearly_weekly_score (UserScore): A full view of the score for a user.
        best_yearly_monthly_score (UserScore): A full view of the score for a user.
        best_yearly_quarterly_score (UserScore): A full view of the score for a user.
        best_lifetime_daily_score (UserScore): A full view of the score for a user.
        best_lifetime_weekly_score (UserScore): A full view of the score for a user.
        best_lifetime_monthly_score (UserScore): A full view of the score for a user.
        best_lifetime_quarterly_score (UserScore): A full view of the score for a user.
        best_lifetime_yearly_score (UserScore): A full view of the score for a user.
    """

    daily_score: "UserScore"
    weekly_score: "UserScore"
    monthly_score: "UserScore"
    quarterly_score: "UserScore"
    yearly_score: "UserScore"
    lifetime_score: "UserScore"
    best_quarterly_daily_score: "UserScore"
    best_quarterly_weekly_score: "UserScore"
    best_quarterly_monthly_score: "UserScore"
    best_yearly_daily_score: "UserScore"
    best_yearly_weekly_score: "UserScore"
    best_yearly_monthly_score: "UserScore"
    best_yearly_quarterly_score: "UserScore"
    best_lifetime_daily_score: "UserScore"
    best_lifetime_weekly_score: "UserScore"
    best_lifetime_monthly_score: "UserScore"
    best_lifetime_quarterly_score: "UserScore"
    best_lifetime_yearly_score: "UserScore"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        daily_score = self.daily_score.to_dict()

        weekly_score = self.weekly_score.to_dict()

        monthly_score = self.monthly_score.to_dict()

        quarterly_score = self.quarterly_score.to_dict()

        yearly_score = self.yearly_score.to_dict()

        lifetime_score = self.lifetime_score.to_dict()

        best_quarterly_daily_score = self.best_quarterly_daily_score.to_dict()

        best_quarterly_weekly_score = self.best_quarterly_weekly_score.to_dict()

        best_quarterly_monthly_score = self.best_quarterly_monthly_score.to_dict()

        best_yearly_daily_score = self.best_yearly_daily_score.to_dict()

        best_yearly_weekly_score = self.best_yearly_weekly_score.to_dict()

        best_yearly_monthly_score = self.best_yearly_monthly_score.to_dict()

        best_yearly_quarterly_score = self.best_yearly_quarterly_score.to_dict()

        best_lifetime_daily_score = self.best_lifetime_daily_score.to_dict()

        best_lifetime_weekly_score = self.best_lifetime_weekly_score.to_dict()

        best_lifetime_monthly_score = self.best_lifetime_monthly_score.to_dict()

        best_lifetime_quarterly_score = self.best_lifetime_quarterly_score.to_dict()

        best_lifetime_yearly_score = self.best_lifetime_yearly_score.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "daily_score": daily_score,
                "weekly_score": weekly_score,
                "monthly_score": monthly_score,
                "quarterly_score": quarterly_score,
                "yearly_score": yearly_score,
                "lifetime_score": lifetime_score,
                "best_quarterly_daily_score": best_quarterly_daily_score,
                "best_quarterly_weekly_score": best_quarterly_weekly_score,
                "best_quarterly_monthly_score": best_quarterly_monthly_score,
                "best_yearly_daily_score": best_yearly_daily_score,
                "best_yearly_weekly_score": best_yearly_weekly_score,
                "best_yearly_monthly_score": best_yearly_monthly_score,
                "best_yearly_quarterly_score": best_yearly_quarterly_score,
                "best_lifetime_daily_score": best_lifetime_daily_score,
                "best_lifetime_weekly_score": best_lifetime_weekly_score,
                "best_lifetime_monthly_score": best_lifetime_monthly_score,
                "best_lifetime_quarterly_score": best_lifetime_quarterly_score,
                "best_lifetime_yearly_score": best_lifetime_yearly_score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_score import UserScore

        d = dict(src_dict)
        daily_score = UserScore.from_dict(d.pop("daily_score"))

        weekly_score = UserScore.from_dict(d.pop("weekly_score"))

        monthly_score = UserScore.from_dict(d.pop("monthly_score"))

        quarterly_score = UserScore.from_dict(d.pop("quarterly_score"))

        yearly_score = UserScore.from_dict(d.pop("yearly_score"))

        lifetime_score = UserScore.from_dict(d.pop("lifetime_score"))

        best_quarterly_daily_score = UserScore.from_dict(d.pop("best_quarterly_daily_score"))

        best_quarterly_weekly_score = UserScore.from_dict(d.pop("best_quarterly_weekly_score"))

        best_quarterly_monthly_score = UserScore.from_dict(d.pop("best_quarterly_monthly_score"))

        best_yearly_daily_score = UserScore.from_dict(d.pop("best_yearly_daily_score"))

        best_yearly_weekly_score = UserScore.from_dict(d.pop("best_yearly_weekly_score"))

        best_yearly_monthly_score = UserScore.from_dict(d.pop("best_yearly_monthly_score"))

        best_yearly_quarterly_score = UserScore.from_dict(d.pop("best_yearly_quarterly_score"))

        best_lifetime_daily_score = UserScore.from_dict(d.pop("best_lifetime_daily_score"))

        best_lifetime_weekly_score = UserScore.from_dict(d.pop("best_lifetime_weekly_score"))

        best_lifetime_monthly_score = UserScore.from_dict(d.pop("best_lifetime_monthly_score"))

        best_lifetime_quarterly_score = UserScore.from_dict(d.pop("best_lifetime_quarterly_score"))

        best_lifetime_yearly_score = UserScore.from_dict(d.pop("best_lifetime_yearly_score"))

        user_score_overview = cls(
            daily_score=daily_score,
            weekly_score=weekly_score,
            monthly_score=monthly_score,
            quarterly_score=quarterly_score,
            yearly_score=yearly_score,
            lifetime_score=lifetime_score,
            best_quarterly_daily_score=best_quarterly_daily_score,
            best_quarterly_weekly_score=best_quarterly_weekly_score,
            best_quarterly_monthly_score=best_quarterly_monthly_score,
            best_yearly_daily_score=best_yearly_daily_score,
            best_yearly_weekly_score=best_yearly_weekly_score,
            best_yearly_monthly_score=best_yearly_monthly_score,
            best_yearly_quarterly_score=best_yearly_quarterly_score,
            best_lifetime_daily_score=best_lifetime_daily_score,
            best_lifetime_weekly_score=best_lifetime_weekly_score,
            best_lifetime_monthly_score=best_lifetime_monthly_score,
            best_lifetime_quarterly_score=best_lifetime_quarterly_score,
            best_lifetime_yearly_score=best_lifetime_yearly_score,
        )

        user_score_overview.additional_properties = d
        return user_score_overview

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
