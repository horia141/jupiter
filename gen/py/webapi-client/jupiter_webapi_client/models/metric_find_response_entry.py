from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

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
        note (Union['Note', None, Unset]):
        metric_entries (Union[None, Unset, list['MetricEntry']]):
        metric_collection_inbox_tasks (Union[None, Unset, list['InboxTask']]):
        metric_entry_notes (Union[None, Unset, list['Note']]):
    """

    metric: "Metric"
    note: Union["Note", None, Unset] = UNSET
    metric_entries: Union[None, Unset, list["MetricEntry"]] = UNSET
    metric_collection_inbox_tasks: Union[None, Unset, list["InboxTask"]] = UNSET
    metric_entry_notes: Union[None, Unset, list["Note"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.note import Note

        metric = self.metric.to_dict()

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        metric_entries: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.metric_entries, Unset):
            metric_entries = UNSET
        elif isinstance(self.metric_entries, list):
            metric_entries = []
            for metric_entries_type_0_item_data in self.metric_entries:
                metric_entries_type_0_item = metric_entries_type_0_item_data.to_dict()
                metric_entries.append(metric_entries_type_0_item)

        else:
            metric_entries = self.metric_entries

        metric_collection_inbox_tasks: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.metric_collection_inbox_tasks, Unset):
            metric_collection_inbox_tasks = UNSET
        elif isinstance(self.metric_collection_inbox_tasks, list):
            metric_collection_inbox_tasks = []
            for metric_collection_inbox_tasks_type_0_item_data in self.metric_collection_inbox_tasks:
                metric_collection_inbox_tasks_type_0_item = metric_collection_inbox_tasks_type_0_item_data.to_dict()
                metric_collection_inbox_tasks.append(metric_collection_inbox_tasks_type_0_item)

        else:
            metric_collection_inbox_tasks = self.metric_collection_inbox_tasks

        metric_entry_notes: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.metric_entry_notes, Unset):
            metric_entry_notes = UNSET
        elif isinstance(self.metric_entry_notes, list):
            metric_entry_notes = []
            for metric_entry_notes_type_0_item_data in self.metric_entry_notes:
                metric_entry_notes_type_0_item = metric_entry_notes_type_0_item_data.to_dict()
                metric_entry_notes.append(metric_entry_notes_type_0_item)

        else:
            metric_entry_notes = self.metric_entry_notes

        field_dict: dict[str, Any] = {}
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.metric import Metric
        from ..models.metric_entry import MetricEntry
        from ..models.note import Note

        d = dict(src_dict)
        metric = Metric.from_dict(d.pop("metric"))

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

        def _parse_metric_entries(data: object) -> Union[None, Unset, list["MetricEntry"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                metric_entries_type_0 = []
                _metric_entries_type_0 = data
                for metric_entries_type_0_item_data in _metric_entries_type_0:
                    metric_entries_type_0_item = MetricEntry.from_dict(metric_entries_type_0_item_data)

                    metric_entries_type_0.append(metric_entries_type_0_item)

                return metric_entries_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["MetricEntry"]], data)

        metric_entries = _parse_metric_entries(d.pop("metric_entries", UNSET))

        def _parse_metric_collection_inbox_tasks(data: object) -> Union[None, Unset, list["InboxTask"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                metric_collection_inbox_tasks_type_0 = []
                _metric_collection_inbox_tasks_type_0 = data
                for metric_collection_inbox_tasks_type_0_item_data in _metric_collection_inbox_tasks_type_0:
                    metric_collection_inbox_tasks_type_0_item = InboxTask.from_dict(
                        metric_collection_inbox_tasks_type_0_item_data
                    )

                    metric_collection_inbox_tasks_type_0.append(metric_collection_inbox_tasks_type_0_item)

                return metric_collection_inbox_tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["InboxTask"]], data)

        metric_collection_inbox_tasks = _parse_metric_collection_inbox_tasks(
            d.pop("metric_collection_inbox_tasks", UNSET)
        )

        def _parse_metric_entry_notes(data: object) -> Union[None, Unset, list["Note"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                metric_entry_notes_type_0 = []
                _metric_entry_notes_type_0 = data
                for metric_entry_notes_type_0_item_data in _metric_entry_notes_type_0:
                    metric_entry_notes_type_0_item = Note.from_dict(metric_entry_notes_type_0_item_data)

                    metric_entry_notes_type_0.append(metric_entry_notes_type_0_item)

                return metric_entry_notes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["Note"]], data)

        metric_entry_notes = _parse_metric_entry_notes(d.pop("metric_entry_notes", UNSET))

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
