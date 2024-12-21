from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.project_update_args_name import ProjectUpdateArgsName


T = TypeVar("T", bound="ProjectUpdateArgs")


@_attrs_define
class ProjectUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (ProjectUpdateArgsName):
    """

    ref_id: str
    name: "ProjectUpdateArgsName"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project_update_args_name import ProjectUpdateArgsName

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = ProjectUpdateArgsName.from_dict(d.pop("name"))

        project_update_args = cls(
            ref_id=ref_id,
            name=name,
        )

        project_update_args.additional_properties = d
        return project_update_args

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
