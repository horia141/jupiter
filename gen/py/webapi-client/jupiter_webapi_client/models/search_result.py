from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.search_match import SearchMatch


T = TypeVar("T", bound="SearchResult")


@_attrs_define
class SearchResult:
    """Search result.

    Attributes:
        search_time (str): A date or possibly a datetime for the application.
        matches (List['SearchMatch']):
    """

    search_time: str
    matches: List["SearchMatch"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        search_time = self.search_time

        matches = []
        for matches_item_data in self.matches:
            matches_item = matches_item_data.to_dict()
            matches.append(matches_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "search_time": search_time,
                "matches": matches,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.search_match import SearchMatch

        d = src_dict.copy()
        search_time = d.pop("search_time")

        matches = []
        _matches = d.pop("matches")
        for matches_item_data in _matches:
            matches_item = SearchMatch.from_dict(matches_item_data)

            matches.append(matches_item)

        search_result = cls(
            search_time=search_time,
            matches=matches,
        )

        search_result.additional_properties = d
        return search_result

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