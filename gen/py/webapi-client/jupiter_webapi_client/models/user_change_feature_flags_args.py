from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_feature import UserFeature

T = TypeVar("T", bound="UserChangeFeatureFlagsArgs")


@_attrs_define
class UserChangeFeatureFlagsArgs:
    """UserChangeFeatureFlags args.

    Attributes:
        feature_flags (List[UserFeature]):
    """

    feature_flags: List[UserFeature]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        feature_flags = []
        for feature_flags_item_data in self.feature_flags:
            feature_flags_item = feature_flags_item_data.value
            feature_flags.append(feature_flags_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "feature_flags": feature_flags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        feature_flags = []
        _feature_flags = d.pop("feature_flags")
        for feature_flags_item_data in _feature_flags:
            feature_flags_item = UserFeature(feature_flags_item_data)

            feature_flags.append(feature_flags_item)

        user_change_feature_flags_args = cls(
            feature_flags=feature_flags,
        )

        user_change_feature_flags_args.additional_properties = d
        return user_change_feature_flags_args

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
