from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Doc")


@_attrs_define
class Doc:
    """A doc in the docbook.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The doc name.
        doc_collection (str):
        archived_time (Union[Unset, str]): A timestamp in the application.
        parent_doc_ref_id (Union[Unset, str]): A generic entity id.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    doc_collection: str
    archived_time: Union[Unset, str] = UNSET
    parent_doc_ref_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        doc_collection = self.doc_collection

        archived_time = self.archived_time

        parent_doc_ref_id = self.parent_doc_ref_id

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
                "doc_collection": doc_collection,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if parent_doc_ref_id is not UNSET:
            field_dict["parent_doc_ref_id"] = parent_doc_ref_id

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

        doc_collection = d.pop("doc_collection")

        archived_time = d.pop("archived_time", UNSET)

        parent_doc_ref_id = d.pop("parent_doc_ref_id", UNSET)

        doc = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            doc_collection=doc_collection,
            archived_time=archived_time,
            parent_doc_ref_id=parent_doc_ref_id,
        )

        doc.additional_properties = d
        return doc

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
