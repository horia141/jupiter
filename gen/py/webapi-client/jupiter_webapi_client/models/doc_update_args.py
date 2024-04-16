from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.doc_update_args_name import DocUpdateArgsName


T = TypeVar("T", bound="DocUpdateArgs")


@_attrs_define
class DocUpdateArgs:
    """DocUpdate args.

    Attributes:
        ref_id (str): A generic entity id.
        name (DocUpdateArgsName):
    """

    ref_id: str
    name: "DocUpdateArgsName"
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
        from ..models.doc_update_args_name import DocUpdateArgsName

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = DocUpdateArgsName.from_dict(d.pop("name"))

        doc_update_args = cls(
            ref_id=ref_id,
            name=name,
        )

        doc_update_args.additional_properties = d
        return doc_update_args

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
