from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectArchiveArgs")


@_attrs_define
class ProjectArchiveArgs:
    """Project archive args.

    Attributes:
        ref_id (str): A generic entity id.
        backup_project_ref_id (Union[None, Unset, str]):
    """

    ref_id: str
    backup_project_ref_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        backup_project_ref_id: Union[None, Unset, str]
        if isinstance(self.backup_project_ref_id, Unset):
            backup_project_ref_id = UNSET
        else:
            backup_project_ref_id = self.backup_project_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
            }
        )
        if backup_project_ref_id is not UNSET:
            field_dict["backup_project_ref_id"] = backup_project_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        def _parse_backup_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        backup_project_ref_id = _parse_backup_project_ref_id(d.pop("backup_project_ref_id", UNSET))

        project_archive_args = cls(
            ref_id=ref_id,
            backup_project_ref_id=backup_project_ref_id,
        )

        project_archive_args.additional_properties = d
        return project_archive_args

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
