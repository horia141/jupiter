from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.metric import Metric
    from ..models.metric_entry import MetricEntry
    from ..models.note import Note


T = TypeVar("T", bound="MetricFindResponseEntry")


@_attrs_define
class MetricFindResponseEntry:
    """A single entry in the LoadAllMetricsResponse.

    Attributes:
        metric (Metric): A metric.
        note (Union[Unset, Note]): A note in the notebook.
        metric_entries (Union[Unset, List['MetricEntry']]):
        metric_collection_inbox_tasks (Union[Unset, List['InboxTask']]):
        metric_entry_notes (Union[Unset, List['Note']]):
    """

    metric: "Metric"
    note: Union[Unset, "Note"] = UNSET
    metric_entries: Union[Unset, List["MetricEntry"]] = UNSET
    metric_collection_inbox_tasks: Union[Unset, List["InboxTask"]] = UNSET
    metric_entry_notes: Union[Unset, List["Note"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metric = self.metric.to_dict()

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        metric_entries: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metric_entries, Unset):
            metric_entries = []
            for metric_entries_item_data in self.metric_entries:
                metric_entries_item = metric_entries_item_data.to_dict()
                metric_entries.append(metric_entries_item)

        metric_collection_inbox_tasks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metric_collection_inbox_tasks, Unset):
            metric_collection_inbox_tasks = []
            for metric_collection_inbox_tasks_item_data in self.metric_collection_inbox_tasks:
                metric_collection_inbox_tasks_item = metric_collection_inbox_tasks_item_data.to_dict()
                metric_collection_inbox_tasks.append(metric_collection_inbox_tasks_item)

        metric_entry_notes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metric_entry_notes, Unset):
            metric_entry_notes = []
            for metric_entry_notes_item_data in self.metric_entry_notes:
                metric_entry_notes_item = metric_entry_notes_item_data.to_dict()
                metric_entry_notes.append(metric_entry_notes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric": metric,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if metric_entries is not UNSET:
            field_dict["metric_entries"] = metric_entries
        if metric_collection_inbox_tasks is not UNSET:
            field_dict["metric_collection_inbox_tasks"] = metric_collection_inbox_tasks
        if metric_entry_notes is not UNSET:
            field_dict["metric_entry_notes"] = metric_entry_notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.metric import Metric
        from ..models.metric_entry import MetricEntry
        from ..models.note import Note

        d = src_dict.copy()
        metric = Metric.from_dict(d.pop("metric"))

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        metric_entries = []
        _metric_entries = d.pop("metric_entries", UNSET)
        for metric_entries_item_data in _metric_entries or []:
            metric_entries_item = MetricEntry.from_dict(metric_entries_item_data)

            metric_entries.append(metric_entries_item)

        metric_collection_inbox_tasks = []
        _metric_collection_inbox_tasks = d.pop("metric_collection_inbox_tasks", UNSET)
        for metric_collection_inbox_tasks_item_data in _metric_collection_inbox_tasks or []:
            metric_collection_inbox_tasks_item = InboxTask.from_dict(metric_collection_inbox_tasks_item_data)

            metric_collection_inbox_tasks.append(metric_collection_inbox_tasks_item)

        metric_entry_notes = []
        _metric_entry_notes = d.pop("metric_entry_notes", UNSET)
        for metric_entry_notes_item_data in _metric_entry_notes or []:
            metric_entry_notes_item = Note.from_dict(metric_entry_notes_item_data)

            metric_entry_notes.append(metric_entry_notes_item)

        metric_find_response_entry = cls(
            metric=metric,
            note=note,
            metric_entries=metric_entries,
            metric_collection_inbox_tasks=metric_collection_inbox_tasks,
            metric_entry_notes=metric_entry_notes,
        )

        metric_find_response_entry.additional_properties = d
        return metric_find_response_entry

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
