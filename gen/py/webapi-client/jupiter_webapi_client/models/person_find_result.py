from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.person_find_result_entry import PersonFindResultEntry
    from ..models.project import Project


T = TypeVar("T", bound="PersonFindResult")


@_attrs_define
class PersonFindResult:
    """PersonFindResult.

    Attributes:
        catch_up_project (Project): The project.
        entries (List['PersonFindResultEntry']):
    """

    catch_up_project: "Project"
    entries: List["PersonFindResultEntry"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        catch_up_project = self.catch_up_project.to_dict()

        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "catch_up_project": catch_up_project,
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.person_find_result_entry import PersonFindResultEntry
        from ..models.project import Project

        d = src_dict.copy()
        catch_up_project = Project.from_dict(d.pop("catch_up_project"))

        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = PersonFindResultEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        person_find_result = cls(
            catch_up_project=catch_up_project,
            entries=entries,
        )

        person_find_result.additional_properties = d
        return person_find_result

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
