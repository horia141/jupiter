from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserWorkspaceLink")


@_attrs_define
class UserWorkspaceLink:
    """A 1:1 link between a user and a workspace.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        user_ref_id (str): A generic entity id.
        workspace_ref_id (str): A generic entity id.
        archived_time (Union[Unset, str]): A timestamp in the application.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    user_ref_id: str
    workspace_ref_id: str
    archived_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        user_ref_id = self.user_ref_id

        workspace_ref_id = self.workspace_ref_id

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
                "user_ref_id": user_ref_id,
                "workspace_ref_id": workspace_ref_id,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        user_ref_id = d.pop("user_ref_id")

        workspace_ref_id = d.pop("workspace_ref_id")

        archived_time = d.pop("archived_time", UNSET)

        user_workspace_link = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            user_ref_id=user_ref_id,
            workspace_ref_id=workspace_ref_id,
            archived_time=archived_time,
        )

        user_workspace_link.additional_properties = d
        return user_workspace_link

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
