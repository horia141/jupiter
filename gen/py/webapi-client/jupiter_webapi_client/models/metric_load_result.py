from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_status import AccessStatus
    from ..models.inbox_task import InboxTask
    from ..models.metric import Metric
    from ..models.metric_entry import MetricEntry
    from ..models.metric_load_metric_entry_tags import MetricLoadMetricEntryTags
    from ..models.metric_load_result_metric_entry_contacts_type_0 import MetricLoadResultMetricEntryContactsType0
    from ..models.note import Note
    from ..models.publish_entity import PublishEntity
    from ..models.tag import Tag
    from ..models.user_light import UserLight


T = TypeVar("T", bound="MetricLoadResult")


@_attrs_define
class MetricLoadResult:
    """MetricLoadResult.

    Attributes:
        metric (Metric): A metric.
        tags (list[Tag]):
        metric_entries (list[MetricEntry]):
        metric_entry_tags (list[MetricLoadMetricEntryTags]):
        collection_tasks (list[InboxTask]):
        collection_tasks_total_cnt (int):
        collection_tasks_page_size (int):
        owner (UserLight): A user's ref id, name, and email address.
        note (None | Note | Unset):
        metric_entry_contacts (MetricLoadResultMetricEntryContactsType0 | None | Unset):
        publish_entity (None | PublishEntity | Unset):
        access_status (AccessStatus | None | Unset):
    """

    metric: Metric
    tags: list[Tag]
    metric_entries: list[MetricEntry]
    metric_entry_tags: list[MetricLoadMetricEntryTags]
    collection_tasks: list[InboxTask]
    collection_tasks_total_cnt: int
    collection_tasks_page_size: int
    owner: UserLight
    note: None | Note | Unset = UNSET
    metric_entry_contacts: MetricLoadResultMetricEntryContactsType0 | None | Unset = UNSET
    publish_entity: None | PublishEntity | Unset = UNSET
    access_status: AccessStatus | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_status import AccessStatus  # noqa: PLC0415
        from ..models.metric_load_result_metric_entry_contacts_type_0 import MetricLoadResultMetricEntryContactsType0  # noqa: PLC0415
        from ..models.note import Note  # noqa: PLC0415
        from ..models.publish_entity import PublishEntity  # noqa: PLC0415

        metric = self.metric.to_dict()

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        metric_entries = []
        for metric_entries_item_data in self.metric_entries:
            metric_entries_item = metric_entries_item_data.to_dict()
            metric_entries.append(metric_entries_item)

        metric_entry_tags = []
        for metric_entry_tags_item_data in self.metric_entry_tags:
            metric_entry_tags_item = metric_entry_tags_item_data.to_dict()
            metric_entry_tags.append(metric_entry_tags_item)

        collection_tasks = []
        for collection_tasks_item_data in self.collection_tasks:
            collection_tasks_item = collection_tasks_item_data.to_dict()
            collection_tasks.append(collection_tasks_item)

        collection_tasks_total_cnt = self.collection_tasks_total_cnt

        collection_tasks_page_size = self.collection_tasks_page_size

        owner = self.owner.to_dict()

        note: dict[str, Any] | None | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        metric_entry_contacts: dict[str, Any] | None | Unset
        if isinstance(self.metric_entry_contacts, Unset):
            metric_entry_contacts = UNSET
        elif isinstance(self.metric_entry_contacts, MetricLoadResultMetricEntryContactsType0):
            metric_entry_contacts = self.metric_entry_contacts.to_dict()
        else:
            metric_entry_contacts = self.metric_entry_contacts

        publish_entity: dict[str, Any] | None | Unset
        if isinstance(self.publish_entity, Unset):
            publish_entity = UNSET
        elif isinstance(self.publish_entity, PublishEntity):
            publish_entity = self.publish_entity.to_dict()
        else:
            publish_entity = self.publish_entity

        access_status: dict[str, Any] | None | Unset
        if isinstance(self.access_status, Unset):
            access_status = UNSET
        elif isinstance(self.access_status, AccessStatus):
            access_status = self.access_status.to_dict()
        else:
            access_status = self.access_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric": metric,
                "tags": tags,
                "metric_entries": metric_entries,
                "metric_entry_tags": metric_entry_tags,
                "collection_tasks": collection_tasks,
                "collection_tasks_total_cnt": collection_tasks_total_cnt,
                "collection_tasks_page_size": collection_tasks_page_size,
                "owner": owner,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if metric_entry_contacts is not UNSET:
            field_dict["metric_entry_contacts"] = metric_entry_contacts
        if publish_entity is not UNSET:
            field_dict["publish_entity"] = publish_entity
        if access_status is not UNSET:
            field_dict["access_status"] = access_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_status import AccessStatus  # noqa: PLC0415
        from ..models.inbox_task import InboxTask  # noqa: PLC0415
        from ..models.metric import Metric  # noqa: PLC0415
        from ..models.metric_entry import MetricEntry  # noqa: PLC0415
        from ..models.metric_load_metric_entry_tags import MetricLoadMetricEntryTags  # noqa: PLC0415
        from ..models.metric_load_result_metric_entry_contacts_type_0 import MetricLoadResultMetricEntryContactsType0  # noqa: PLC0415
        from ..models.note import Note  # noqa: PLC0415
        from ..models.publish_entity import PublishEntity  # noqa: PLC0415
        from ..models.tag import Tag  # noqa: PLC0415
        from ..models.user_light import UserLight  # noqa: PLC0415

        d = dict(src_dict)
        metric = Metric.from_dict(d.pop("metric"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        metric_entries = []
        _metric_entries = d.pop("metric_entries")
        for metric_entries_item_data in _metric_entries:
            metric_entries_item = MetricEntry.from_dict(metric_entries_item_data)

            metric_entries.append(metric_entries_item)

        metric_entry_tags = []
        _metric_entry_tags = d.pop("metric_entry_tags")
        for metric_entry_tags_item_data in _metric_entry_tags:
            metric_entry_tags_item = MetricLoadMetricEntryTags.from_dict(metric_entry_tags_item_data)

            metric_entry_tags.append(metric_entry_tags_item)

        collection_tasks = []
        _collection_tasks = d.pop("collection_tasks")
        for collection_tasks_item_data in _collection_tasks:
            collection_tasks_item = InboxTask.from_dict(collection_tasks_item_data)

            collection_tasks.append(collection_tasks_item)

        collection_tasks_total_cnt = d.pop("collection_tasks_total_cnt")

        collection_tasks_page_size = d.pop("collection_tasks_page_size")

        owner = UserLight.from_dict(d.pop("owner"))

        def _parse_note(data: object) -> None | Note | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Note | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_metric_entry_contacts(data: object) -> MetricLoadResultMetricEntryContactsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metric_entry_contacts_type_0 = MetricLoadResultMetricEntryContactsType0.from_dict(data)

                return metric_entry_contacts_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MetricLoadResultMetricEntryContactsType0 | None | Unset, data)

        metric_entry_contacts = _parse_metric_entry_contacts(d.pop("metric_entry_contacts", UNSET))

        def _parse_publish_entity(data: object) -> None | PublishEntity | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                publish_entity_type_0 = PublishEntity.from_dict(data)

                return publish_entity_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PublishEntity | Unset, data)

        publish_entity = _parse_publish_entity(d.pop("publish_entity", UNSET))

        def _parse_access_status(data: object) -> AccessStatus | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                access_status_type_0 = AccessStatus.from_dict(data)

                return access_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccessStatus | None | Unset, data)

        access_status = _parse_access_status(d.pop("access_status", UNSET))

        metric_load_result = cls(
            metric=metric,
            tags=tags,
            metric_entries=metric_entries,
            metric_entry_tags=metric_entry_tags,
            collection_tasks=collection_tasks,
            collection_tasks_total_cnt=collection_tasks_total_cnt,
            collection_tasks_page_size=collection_tasks_page_size,
            owner=owner,
            note=note,
            metric_entry_contacts=metric_entry_contacts,
            publish_entity=publish_entity,
            access_status=access_status,
        )

        metric_load_result.additional_properties = d
        return metric_load_result

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
