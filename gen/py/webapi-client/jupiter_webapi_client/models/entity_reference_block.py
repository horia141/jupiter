from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.entity_reference_block_kind import EntityReferenceBlockKind
from ..models.named_entity_tag import NamedEntityTag

T = TypeVar("T", bound="EntityReferenceBlock")


@_attrs_define
class EntityReferenceBlock:
    """A link.

    Attributes:
        correlation_id (str): A generic entity id.
        kind (EntityReferenceBlockKind):
        entity_tag (NamedEntityTag): A tag for all known entities.
        ref_id (str): A generic entity id.
    """

    correlation_id: str
    kind: EntityReferenceBlockKind
    entity_tag: NamedEntityTag
    ref_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        correlation_id = self.correlation_id

        kind = self.kind.value

        entity_tag = self.entity_tag.value

        ref_id = self.ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "kind": kind,
                "entity_tag": entity_tag,
                "ref_id": ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        correlation_id = d.pop("correlation_id")

        kind = EntityReferenceBlockKind(d.pop("kind"))

        entity_tag = NamedEntityTag(d.pop("entity_tag"))

        ref_id = d.pop("ref_id")

        entity_reference_block = cls(
            correlation_id=correlation_id,
            kind=kind,
            entity_tag=entity_tag,
            ref_id=ref_id,
        )

        entity_reference_block.additional_properties = d
        return entity_reference_block

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
