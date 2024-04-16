from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocFindArgs")


@_attrs_define
class DocFindArgs:
    """DocFind args.

    Attributes:
        include_notes (bool):
        allow_archived (bool):
        include_subdocs (bool):
        filter_ref_ids (Union[Unset, List[str]]):
    """

    include_notes: bool
    allow_archived: bool
    include_subdocs: bool
    filter_ref_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        include_notes = self.include_notes

        allow_archived = self.allow_archived

        include_subdocs = self.include_subdocs

        filter_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_ref_ids, Unset):
            filter_ref_ids = self.filter_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "include_notes": include_notes,
                "allow_archived": allow_archived,
                "include_subdocs": include_subdocs,
            }
        )
        if filter_ref_ids is not UNSET:
            field_dict["filter_ref_ids"] = filter_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        include_notes = d.pop("include_notes")

        allow_archived = d.pop("allow_archived")

        include_subdocs = d.pop("include_subdocs")

        filter_ref_ids = cast(List[str], d.pop("filter_ref_ids", UNSET))

        doc_find_args = cls(
            include_notes=include_notes,
            allow_archived=allow_archived,
            include_subdocs=include_subdocs,
            filter_ref_ids=filter_ref_ids,
        )

        doc_find_args.additional_properties = d
        return doc_find_args

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
