from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_feature import UserFeature
from ..models.workspace_feature import WorkspaceFeature
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.widget_type_constraints_allowed_dimensions import WidgetTypeConstraintsAllowedDimensions


T = TypeVar("T", bound="WidgetTypeConstraints")


@_attrs_define
class WidgetTypeConstraints:
    """A constraints for a widget type.

    Attributes:
        allowed_dimensions (WidgetTypeConstraintsAllowedDimensions):
        only_for_workspace_features (list[WorkspaceFeature] | None | Unset):
        only_for_user_features (list[UserFeature] | None | Unset):
    """

    allowed_dimensions: WidgetTypeConstraintsAllowedDimensions
    only_for_workspace_features: list[WorkspaceFeature] | None | Unset = UNSET
    only_for_user_features: list[UserFeature] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_dimensions = self.allowed_dimensions.to_dict()

        only_for_workspace_features: list[str] | None | Unset
        if isinstance(self.only_for_workspace_features, Unset):
            only_for_workspace_features = UNSET
        elif isinstance(self.only_for_workspace_features, list):
            only_for_workspace_features = []
            for only_for_workspace_features_type_0_item_data in self.only_for_workspace_features:
                only_for_workspace_features_type_0_item = only_for_workspace_features_type_0_item_data.value
                only_for_workspace_features.append(only_for_workspace_features_type_0_item)

        else:
            only_for_workspace_features = self.only_for_workspace_features

        only_for_user_features: list[str] | None | Unset
        if isinstance(self.only_for_user_features, Unset):
            only_for_user_features = UNSET
        elif isinstance(self.only_for_user_features, list):
            only_for_user_features = []
            for only_for_user_features_type_0_item_data in self.only_for_user_features:
                only_for_user_features_type_0_item = only_for_user_features_type_0_item_data.value
                only_for_user_features.append(only_for_user_features_type_0_item)

        else:
            only_for_user_features = self.only_for_user_features

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allowed_dimensions": allowed_dimensions,
            }
        )
        if only_for_workspace_features is not UNSET:
            field_dict["only_for_workspace_features"] = only_for_workspace_features
        if only_for_user_features is not UNSET:
            field_dict["only_for_user_features"] = only_for_user_features

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_type_constraints_allowed_dimensions import WidgetTypeConstraintsAllowedDimensions  # noqa: PLC0415

        d = dict(src_dict)
        allowed_dimensions = WidgetTypeConstraintsAllowedDimensions.from_dict(d.pop("allowed_dimensions"))

        def _parse_only_for_workspace_features(data: object) -> list[WorkspaceFeature] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                only_for_workspace_features_type_0 = []
                _only_for_workspace_features_type_0 = data
                for only_for_workspace_features_type_0_item_data in _only_for_workspace_features_type_0:
                    only_for_workspace_features_type_0_item = WorkspaceFeature(
                        only_for_workspace_features_type_0_item_data
                    )

                    only_for_workspace_features_type_0.append(only_for_workspace_features_type_0_item)

                return only_for_workspace_features_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[WorkspaceFeature] | None | Unset, data)

        only_for_workspace_features = _parse_only_for_workspace_features(d.pop("only_for_workspace_features", UNSET))

        def _parse_only_for_user_features(data: object) -> list[UserFeature] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                only_for_user_features_type_0 = []
                _only_for_user_features_type_0 = data
                for only_for_user_features_type_0_item_data in _only_for_user_features_type_0:
                    only_for_user_features_type_0_item = UserFeature(only_for_user_features_type_0_item_data)

                    only_for_user_features_type_0.append(only_for_user_features_type_0_item)

                return only_for_user_features_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[UserFeature] | None | Unset, data)

        only_for_user_features = _parse_only_for_user_features(d.pop("only_for_user_features", UNSET))

        widget_type_constraints = cls(
            allowed_dimensions=allowed_dimensions,
            only_for_workspace_features=only_for_workspace_features,
            only_for_user_features=only_for_user_features,
        )

        widget_type_constraints.additional_properties = d
        return widget_type_constraints

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
