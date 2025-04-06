from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metric_find_response_entry import MetricFindResponseEntry
    from ..models.project import Project


T = TypeVar("T", bound="MetricFindResult")


@_attrs_define
class MetricFindResult:
    """PersonFindResult object.

    Attributes:
        collection_project (Project): The project.
        entries (list['MetricFindResponseEntry']):
    """

    collection_project: "Project"
    entries: list["MetricFindResponseEntry"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection_project = self.collection_project.to_dict()

        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "collection_project": collection_project,
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metric_find_response_entry import MetricFindResponseEntry
        from ..models.project import Project

        d = dict(src_dict)
        collection_project = Project.from_dict(d.pop("collection_project"))

        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = MetricFindResponseEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        metric_find_result = cls(
            collection_project=collection_project,
            entries=entries,
        )

        metric_find_result.additional_properties = d
        return metric_find_result

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
