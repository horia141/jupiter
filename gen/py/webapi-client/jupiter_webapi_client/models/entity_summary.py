from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.named_entity_tag import NamedEntityTag
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySummary")


@_attrs_define
class EntitySummary:
    """Information about a particular entity very broadly.

    Attributes:
        entity_tag (NamedEntityTag): A tag for all known entities.
        parent_ref_id (str): A generic entity id.
        ref_id (str): A generic entity id.
        name (str): The name for an entity which acts as both name and unique identifier.
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        snippet (str):
        archived_time (Union[None, Unset, str]):
    """

    entity_tag: NamedEntityTag
    parent_ref_id: str
    ref_id: str
    name: str
    archived: bool
    created_time: str
    last_modified_time: str
    snippet: str
    archived_time: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        entity_tag = self.entity_tag.value

        parent_ref_id = self.parent_ref_id

        ref_id = self.ref_id

        name = self.name

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        snippet = self.snippet

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entity_tag": entity_tag,
                "parent_ref_id": parent_ref_id,
                "ref_id": ref_id,
                "name": name,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "snippet": snippet,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        entity_tag = NamedEntityTag(d.pop("entity_tag"))

        parent_ref_id = d.pop("parent_ref_id")

        ref_id = d.pop("ref_id")

        name = d.pop("name")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        snippet = d.pop("snippet")

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        entity_summary = cls(
            entity_tag=entity_tag,
            parent_ref_id=parent_ref_id,
            ref_id=ref_id,
            name=name,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            snippet=snippet,
            archived_time=archived_time,
        )

        entity_summary.additional_properties = d
        return entity_summary

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
