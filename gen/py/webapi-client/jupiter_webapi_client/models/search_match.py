from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.entity_summary import EntitySummary


T = TypeVar("T", bound="SearchMatch")


@_attrs_define
class SearchMatch:
    """Information about a particular entity that was found.

    Attributes:
        summary (EntitySummary): Information about a particular entity very broadly.
        search_rank (float):
    """

    summary: "EntitySummary"
    search_rank: float
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        summary = self.summary.to_dict()

        search_rank = self.search_rank

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "summary": summary,
                "search_rank": search_rank,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entity_summary import EntitySummary

        d = src_dict.copy()
        summary = EntitySummary.from_dict(d.pop("summary"))

        search_rank = d.pop("search_rank")

        search_match = cls(
            summary=summary,
            search_rank=search_rank,
        )

        search_match.additional_properties = d
        return search_match

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
