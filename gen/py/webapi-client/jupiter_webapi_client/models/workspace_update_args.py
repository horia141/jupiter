from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workspace_update_args_name import WorkspaceUpdateArgsName


T = TypeVar("T", bound="WorkspaceUpdateArgs")


@_attrs_define
class WorkspaceUpdateArgs:
    """PersonFindArgs.

    Attributes:
        name (WorkspaceUpdateArgsName):
    """

    name: "WorkspaceUpdateArgsName"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workspace_update_args_name import WorkspaceUpdateArgsName

        d = dict(src_dict)
        name = WorkspaceUpdateArgsName.from_dict(d.pop("name"))

        workspace_update_args = cls(
            name=name,
        )

        workspace_update_args.additional_properties = d
        return workspace_update_args

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
