from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_category import UserCategory
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_feature_flags import UserFeatureFlags


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """A user of jupiter.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        category (UserCategory): The category of user.
        email_address (str): An email address.
        name (str): The user name for a user of jupiter.
        avatar (str): A user avatar image.
        timezone (str): A timezone in this domain.
        feature_flags (UserFeatureFlags):
        archived_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    category: UserCategory
    email_address: str
    name: str
    avatar: str
    timezone: str
    feature_flags: "UserFeatureFlags"
    archived_time: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        category = self.category.value

        email_address = self.email_address

        name = self.name

        avatar = self.avatar

        timezone = self.timezone

        feature_flags = self.feature_flags.to_dict()

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "category": category,
                "email_address": email_address,
                "name": name,
                "avatar": avatar,
                "timezone": timezone,
                "feature_flags": feature_flags,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_feature_flags import UserFeatureFlags

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        category = UserCategory(d.pop("category"))

        email_address = d.pop("email_address")

        name = d.pop("name")

        avatar = d.pop("avatar")

        timezone = d.pop("timezone")

        feature_flags = UserFeatureFlags.from_dict(d.pop("feature_flags"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        user = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            category=category,
            email_address=email_address,
            name=name,
            avatar=avatar,
            timezone=timezone,
            feature_flags=feature_flags,
            archived_time=archived_time,
        )

        user.additional_properties = d
        return user

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
