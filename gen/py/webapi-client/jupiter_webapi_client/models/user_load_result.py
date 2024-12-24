from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

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
        user (User): A user of jupiter.
        user_score_overview (Union['UserScoreOverview', None, Unset]):
        user_score_history (Union['UserScoreHistory', None, Unset]):
    """

    user: "User"
    user_score_overview: Union["UserScoreOverview", None, Unset] = UNSET
    user_score_history: Union["UserScoreHistory", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.user_score_history import UserScoreHistory
        from ..models.user_score_overview import UserScoreOverview

        user = self.user.to_dict()

        user_score_overview: Union[Dict[str, Any], None, Unset]
        if isinstance(self.user_score_overview, Unset):
            user_score_overview = UNSET
        elif isinstance(self.user_score_overview, UserScoreOverview):
            user_score_overview = self.user_score_overview.to_dict()
        else:
            user_score_overview = self.user_score_overview

        user_score_history: Union[Dict[str, Any], None, Unset]
        if isinstance(self.user_score_history, Unset):
            user_score_history = UNSET
        elif isinstance(self.user_score_history, UserScoreHistory):
            user_score_history = self.user_score_history.to_dict()
        else:
            user_score_history = self.user_score_history

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

        def _parse_user_score_overview(data: object) -> Union["UserScoreOverview", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_score_overview_type_0 = UserScoreOverview.from_dict(data)

                return user_score_overview_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UserScoreOverview", None, Unset], data)

        user_score_overview = _parse_user_score_overview(d.pop("user_score_overview", UNSET))

        def _parse_user_score_history(data: object) -> Union["UserScoreHistory", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_score_history_type_0 = UserScoreHistory.from_dict(data)

                return user_score_history_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UserScoreHistory", None, Unset], data)

        user_score_history = _parse_user_score_history(d.pop("user_score_history", UNSET))

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
