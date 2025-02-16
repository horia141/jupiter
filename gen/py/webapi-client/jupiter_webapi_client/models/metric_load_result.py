from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.metric import Metric
    from ..models.metric_entry import MetricEntry
    from ..models.note import Note


T = TypeVar("T", bound="MetricLoadResult")


@_attrs_define
class MetricLoadResult:
    """MetricLoadResult.

    Attributes:
        metric (Metric): A metric.
        metric_entries (List['MetricEntry']):
        collection_tasks (List['InboxTask']):
        collection_tasks_total_cnt (int):
        collection_tasks_page_size (int):
        note (Union['Note', None, Unset]):
    """

    metric: "Metric"
    metric_entries: List["MetricEntry"]
    collection_tasks: List["InboxTask"]
    collection_tasks_total_cnt: int
    collection_tasks_page_size: int
    note: Union["Note", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.note import Note

        metric = self.metric.to_dict()

        metric_entries = []
        for metric_entries_item_data in self.metric_entries:
            metric_entries_item = metric_entries_item_data.to_dict()
            metric_entries.append(metric_entries_item)

        collection_tasks = []
        for collection_tasks_item_data in self.collection_tasks:
            collection_tasks_item = collection_tasks_item_data.to_dict()
            collection_tasks.append(collection_tasks_item)

        collection_tasks_total_cnt = self.collection_tasks_total_cnt

        collection_tasks_page_size = self.collection_tasks_page_size

        note: Union[Dict[str, Any], None, Unset]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric": metric,
                "metric_entries": metric_entries,
                "collection_tasks": collection_tasks,
                "collection_tasks_total_cnt": collection_tasks_total_cnt,
                "collection_tasks_page_size": collection_tasks_page_size,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.metric import Metric
        from ..models.metric_entry import MetricEntry
        from ..models.note import Note

        d = src_dict.copy()
        metric = Metric.from_dict(d.pop("metric"))

        metric_entries = []
        _metric_entries = d.pop("metric_entries")
        for metric_entries_item_data in _metric_entries:
            metric_entries_item = MetricEntry.from_dict(metric_entries_item_data)

            metric_entries.append(metric_entries_item)

        collection_tasks = []
        _collection_tasks = d.pop("collection_tasks")
        for collection_tasks_item_data in _collection_tasks:
            collection_tasks_item = InboxTask.from_dict(collection_tasks_item_data)

            collection_tasks.append(collection_tasks_item)

        collection_tasks_total_cnt = d.pop("collection_tasks_total_cnt")

        collection_tasks_page_size = d.pop("collection_tasks_page_size")

        def _parse_note(data: object) -> Union["Note", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Note", None, Unset], data)

        note = _parse_note(d.pop("note", UNSET))

        metric_load_result = cls(
            metric=metric,
            metric_entries=metric_entries,
            collection_tasks=collection_tasks,
            collection_tasks_total_cnt=collection_tasks_total_cnt,
            collection_tasks_page_size=collection_tasks_page_size,
            note=note,
        )

        metric_load_result.additional_properties = d
        return metric_load_result

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
