from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """The project.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The project name.
        project_collection_ref_id (str):
        order_of_child_projects (List[str]):
        archived_time (Union[None, Unset, str]):
        parent_project_ref_id (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    project_collection_ref_id: str
    order_of_child_projects: List[str]
    archived_time: Union[None, Unset, str] = UNSET
    parent_project_ref_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        project_collection_ref_id = self.project_collection_ref_id

        order_of_child_projects = self.order_of_child_projects

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        parent_project_ref_id: Union[None, Unset, str]
        if isinstance(self.parent_project_ref_id, Unset):
            parent_project_ref_id = UNSET
        else:
            parent_project_ref_id = self.parent_project_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "project_collection_ref_id": project_collection_ref_id,
                "order_of_child_projects": order_of_child_projects,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if parent_project_ref_id is not UNSET:
            field_dict["parent_project_ref_id"] = parent_project_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        project_collection_ref_id = d.pop("project_collection_ref_id")

        order_of_child_projects = cast(List[str], d.pop("order_of_child_projects"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_parent_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_project_ref_id = _parse_parent_project_ref_id(d.pop("parent_project_ref_id", UNSET))

        project = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            project_collection_ref_id=project_collection_ref_id,
            order_of_child_projects=order_of_child_projects,
            archived_time=archived_time,
            parent_project_ref_id=parent_project_ref_id,
        )

        project.additional_properties = d
        return project

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
