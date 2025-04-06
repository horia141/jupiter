from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_feature import UserFeature

T = TypeVar("T", bound="UserChangeFeatureFlagsArgs")


@_attrs_define
class UserChangeFeatureFlagsArgs:
    """UserChangeFeatureFlags args.

    Attributes:
        feature_flags (list[UserFeature]):
    """

    feature_flags: list[UserFeature]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        feature_flags = []
        for feature_flags_item_data in self.feature_flags:
            feature_flags_item = feature_flags_item_data.value
            feature_flags.append(feature_flags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "feature_flags": feature_flags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
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
