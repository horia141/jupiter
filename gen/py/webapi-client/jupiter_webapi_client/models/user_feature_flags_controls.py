from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_feature_flags_controls_controls import UserFeatureFlagsControlsControls


T = TypeVar("T", bound="UserFeatureFlagsControls")


@_attrs_define
class UserFeatureFlagsControls:
    """Feature settings controls for the user.

    Attributes:
        controls (UserFeatureFlagsControlsControls):
    """

    controls: "UserFeatureFlagsControlsControls"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        controls = self.controls.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "controls": controls,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_feature_flags_controls_controls import UserFeatureFlagsControlsControls

        d = dict(src_dict)
        controls = UserFeatureFlagsControlsControls.from_dict(d.pop("controls"))

        user_feature_flags_controls = cls(
            controls=controls,
        )

        user_feature_flags_controls.additional_properties = d
        return user_feature_flags_controls

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
