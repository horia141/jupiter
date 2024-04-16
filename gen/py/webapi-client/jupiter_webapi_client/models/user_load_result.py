from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User
    from ..models.user_score_history import UserScoreHistory
    from ..models.user_score_overview import UserScoreOverview


T = TypeVar("T", bound="UserLoadResult")


@_attrs_define
class UserLoadResult:
    """User find result.

    Attributes:
        user (User): A user of Jupiter.
        user_score_overview (Union[Unset, UserScoreOverview]): An overview of the scores for a user.
        user_score_history (Union[Unset, UserScoreHistory]): A history of user scores over time.
    """

    user: "User"
    user_score_overview: Union[Unset, "UserScoreOverview"] = UNSET
    user_score_history: Union[Unset, "UserScoreHistory"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user = self.user.to_dict()

        user_score_overview: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user_score_overview, Unset):
            user_score_overview = self.user_score_overview.to_dict()

        user_score_history: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user_score_history, Unset):
            user_score_history = self.user_score_history.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
            }
        )
        if user_score_overview is not UNSET:
            field_dict["user_score_overview"] = user_score_overview
        if user_score_history is not UNSET:
            field_dict["user_score_history"] = user_score_history

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user import User
        from ..models.user_score_history import UserScoreHistory
        from ..models.user_score_overview import UserScoreOverview

        d = src_dict.copy()
        user = User.from_dict(d.pop("user"))

        _user_score_overview = d.pop("user_score_overview", UNSET)
        user_score_overview: Union[Unset, UserScoreOverview]
        if isinstance(_user_score_overview, Unset):
            user_score_overview = UNSET
        else:
            user_score_overview = UserScoreOverview.from_dict(_user_score_overview)

        _user_score_history = d.pop("user_score_history", UNSET)
        user_score_history: Union[Unset, UserScoreHistory]
        if isinstance(_user_score_history, Unset):
            user_score_history = UNSET
        else:
            user_score_history = UserScoreHistory.from_dict(_user_score_history)

        user_load_result = cls(
            user=user,
            user_score_overview=user_score_overview,
            user_score_history=user_score_history,
        )

        user_load_result.additional_properties = d
        return user_load_result

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
