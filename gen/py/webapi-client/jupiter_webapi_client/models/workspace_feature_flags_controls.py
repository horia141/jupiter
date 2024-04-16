from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workspace_feature_flags_controls_controls import WorkspaceFeatureFlagsControlsControls


T = TypeVar("T", bound="WorkspaceFeatureFlagsControls")


@_attrs_define
class WorkspaceFeatureFlagsControls:
    """Feature settings controls for the workspace.

    Attributes:
        controls (WorkspaceFeatureFlagsControlsControls):
    """

    controls: "WorkspaceFeatureFlagsControlsControls"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        controls = self.controls.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "controls": controls,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.workspace_feature_flags_controls_controls import WorkspaceFeatureFlagsControlsControls

        d = src_dict.copy()
        controls = WorkspaceFeatureFlagsControlsControls.from_dict(d.pop("controls"))

        workspace_feature_flags_controls = cls(
            controls=controls,
        )

        workspace_feature_flags_controls.additional_properties = d
        return workspace_feature_flags_controls

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
