from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_summary import EntitySummary


T = TypeVar("T", bound="GenLogEntry")


@_attrs_define
class GenLogEntry:
    """A particular entry in the task generation log.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        gen_log_ref_id (str):
        source (EventSource): The source of the modification which this event records.
        gen_even_if_not_modified (bool):
        today (str): A date or possibly a datetime for the application.
        gen_targets (list[SyncTarget]):
        opened (bool):
        entity_created_records (list['EntitySummary']):
        entity_updated_records (list['EntitySummary']):
        entity_removed_records (list['EntitySummary']):
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        period (Union[None, Unset, list[RecurringTaskPeriod]]):
        filter_project_ref_ids (Union[None, Unset, list[str]]):
        filter_habit_ref_ids (Union[None, Unset, list[str]]):
        filter_chore_ref_ids (Union[None, Unset, list[str]]):
        filter_metric_ref_ids (Union[None, Unset, list[str]]):
        filter_person_ref_ids (Union[None, Unset, list[str]]):
        filter_slack_task_ref_ids (Union[None, Unset, list[str]]):
        filter_email_task_ref_ids (Union[None, Unset, list[str]]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    gen_log_ref_id: str
    source: EventSource
    gen_even_if_not_modified: bool
    today: str
    gen_targets: list[SyncTarget]
    opened: bool
    entity_created_records: list["EntitySummary"]
    entity_updated_records: list["EntitySummary"]
    entity_removed_records: list["EntitySummary"]
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    period: Union[None, Unset, list[RecurringTaskPeriod]] = UNSET
    filter_project_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_habit_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_chore_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_metric_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_person_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_slack_task_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_email_task_ref_ids: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        gen_log_ref_id = self.gen_log_ref_id

        source = self.source.value

        gen_even_if_not_modified = self.gen_even_if_not_modified

        today = self.today

        gen_targets = []
        for gen_targets_item_data in self.gen_targets:
            gen_targets_item = gen_targets_item_data.value
            gen_targets.append(gen_targets_item)

        opened = self.opened

        entity_created_records = []
        for entity_created_records_item_data in self.entity_created_records:
            entity_created_records_item = entity_created_records_item_data.to_dict()
            entity_created_records.append(entity_created_records_item)

        entity_updated_records = []
        for entity_updated_records_item_data in self.entity_updated_records:
            entity_updated_records_item = entity_updated_records_item_data.to_dict()
            entity_updated_records.append(entity_updated_records_item)

        entity_removed_records = []
        for entity_removed_records_item_data in self.entity_removed_records:
            entity_removed_records_item = entity_removed_records_item_data.to_dict()
            entity_removed_records.append(entity_removed_records_item)

        archival_reason: Union[None, Unset, str]
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        period: Union[None, Unset, list[str]]
        if isinstance(self.period, Unset):
            period = UNSET
        elif isinstance(self.period, list):
            period = []
            for period_type_0_item_data in self.period:
                period_type_0_item = period_type_0_item_data.value
                period.append(period_type_0_item)

        else:
            period = self.period

        filter_project_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = UNSET
        elif isinstance(self.filter_project_ref_ids, list):
            filter_project_ref_ids = self.filter_project_ref_ids

        else:
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_habit_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = UNSET
        elif isinstance(self.filter_habit_ref_ids, list):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        else:
            filter_habit_ref_ids = self.filter_habit_ref_ids

        filter_chore_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_chore_ref_ids, Unset):
            filter_chore_ref_ids = UNSET
        elif isinstance(self.filter_chore_ref_ids, list):
            filter_chore_ref_ids = self.filter_chore_ref_ids

        else:
            filter_chore_ref_ids = self.filter_chore_ref_ids

        filter_metric_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_metric_ref_ids, Unset):
            filter_metric_ref_ids = UNSET
        elif isinstance(self.filter_metric_ref_ids, list):
            filter_metric_ref_ids = self.filter_metric_ref_ids

        else:
            filter_metric_ref_ids = self.filter_metric_ref_ids

        filter_person_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_person_ref_ids, Unset):
            filter_person_ref_ids = UNSET
        elif isinstance(self.filter_person_ref_ids, list):
            filter_person_ref_ids = self.filter_person_ref_ids

        else:
            filter_person_ref_ids = self.filter_person_ref_ids

        filter_slack_task_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_slack_task_ref_ids, Unset):
            filter_slack_task_ref_ids = UNSET
        elif isinstance(self.filter_slack_task_ref_ids, list):
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        else:
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        filter_email_task_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_email_task_ref_ids, Unset):
            filter_email_task_ref_ids = UNSET
        elif isinstance(self.filter_email_task_ref_ids, list):
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        else:
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "gen_log_ref_id": gen_log_ref_id,
                "source": source,
                "gen_even_if_not_modified": gen_even_if_not_modified,
                "today": today,
                "gen_targets": gen_targets,
                "opened": opened,
                "entity_created_records": entity_created_records,
                "entity_updated_records": entity_updated_records,
                "entity_removed_records": entity_removed_records,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if period is not UNSET:
            field_dict["period"] = period
        if filter_project_ref_ids is not UNSET:
            field_dict["filter_project_ref_ids"] = filter_project_ref_ids
        if filter_habit_ref_ids is not UNSET:
            field_dict["filter_habit_ref_ids"] = filter_habit_ref_ids
        if filter_chore_ref_ids is not UNSET:
            field_dict["filter_chore_ref_ids"] = filter_chore_ref_ids
        if filter_metric_ref_ids is not UNSET:
            field_dict["filter_metric_ref_ids"] = filter_metric_ref_ids
        if filter_person_ref_ids is not UNSET:
            field_dict["filter_person_ref_ids"] = filter_person_ref_ids
        if filter_slack_task_ref_ids is not UNSET:
            field_dict["filter_slack_task_ref_ids"] = filter_slack_task_ref_ids
        if filter_email_task_ref_ids is not UNSET:
            field_dict["filter_email_task_ref_ids"] = filter_email_task_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_summary import EntitySummary

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        gen_log_ref_id = d.pop("gen_log_ref_id")

        source = EventSource(d.pop("source"))

        gen_even_if_not_modified = d.pop("gen_even_if_not_modified")

        today = d.pop("today")

        gen_targets = []
        _gen_targets = d.pop("gen_targets")
        for gen_targets_item_data in _gen_targets:
            gen_targets_item = SyncTarget(gen_targets_item_data)

            gen_targets.append(gen_targets_item)

        opened = d.pop("opened")

        entity_created_records = []
        _entity_created_records = d.pop("entity_created_records")
        for entity_created_records_item_data in _entity_created_records:
            entity_created_records_item = EntitySummary.from_dict(entity_created_records_item_data)

            entity_created_records.append(entity_created_records_item)

        entity_updated_records = []
        _entity_updated_records = d.pop("entity_updated_records")
        for entity_updated_records_item_data in _entity_updated_records:
            entity_updated_records_item = EntitySummary.from_dict(entity_updated_records_item_data)

            entity_updated_records.append(entity_updated_records_item)

        entity_removed_records = []
        _entity_removed_records = d.pop("entity_removed_records")
        for entity_removed_records_item_data in _entity_removed_records:
            entity_removed_records_item = EntitySummary.from_dict(entity_removed_records_item_data)

            entity_removed_records.append(entity_removed_records_item)

        def _parse_archival_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_period(data: object) -> Union[None, Unset, list[RecurringTaskPeriod]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                period_type_0 = []
                _period_type_0 = data
                for period_type_0_item_data in _period_type_0:
                    period_type_0_item = RecurringTaskPeriod(period_type_0_item_data)

                    period_type_0.append(period_type_0_item)

                return period_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[RecurringTaskPeriod]], data)

        period = _parse_period(d.pop("period", UNSET))

        def _parse_filter_project_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_project_ref_ids_type_0 = cast(list[str], data)

                return filter_project_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_project_ref_ids = _parse_filter_project_ref_ids(d.pop("filter_project_ref_ids", UNSET))

        def _parse_filter_habit_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_habit_ref_ids_type_0 = cast(list[str], data)

                return filter_habit_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_habit_ref_ids = _parse_filter_habit_ref_ids(d.pop("filter_habit_ref_ids", UNSET))

        def _parse_filter_chore_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_chore_ref_ids_type_0 = cast(list[str], data)

                return filter_chore_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_chore_ref_ids = _parse_filter_chore_ref_ids(d.pop("filter_chore_ref_ids", UNSET))

        def _parse_filter_metric_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_metric_ref_ids_type_0 = cast(list[str], data)

                return filter_metric_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_metric_ref_ids = _parse_filter_metric_ref_ids(d.pop("filter_metric_ref_ids", UNSET))

        def _parse_filter_person_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_person_ref_ids_type_0 = cast(list[str], data)

                return filter_person_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_person_ref_ids = _parse_filter_person_ref_ids(d.pop("filter_person_ref_ids", UNSET))

        def _parse_filter_slack_task_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_slack_task_ref_ids_type_0 = cast(list[str], data)

                return filter_slack_task_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_slack_task_ref_ids = _parse_filter_slack_task_ref_ids(d.pop("filter_slack_task_ref_ids", UNSET))

        def _parse_filter_email_task_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_email_task_ref_ids_type_0 = cast(list[str], data)

                return filter_email_task_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_email_task_ref_ids = _parse_filter_email_task_ref_ids(d.pop("filter_email_task_ref_ids", UNSET))

        gen_log_entry = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            gen_log_ref_id=gen_log_ref_id,
            source=source,
            gen_even_if_not_modified=gen_even_if_not_modified,
            today=today,
            gen_targets=gen_targets,
            opened=opened,
            entity_created_records=entity_created_records,
            entity_updated_records=entity_updated_records,
            entity_removed_records=entity_removed_records,
            archival_reason=archival_reason,
            archived_time=archived_time,
            period=period,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_habit_ref_ids=filter_habit_ref_ids,
            filter_chore_ref_ids=filter_chore_ref_ids,
            filter_metric_ref_ids=filter_metric_ref_ids,
            filter_person_ref_ids=filter_person_ref_ids,
            filter_slack_task_ref_ids=filter_slack_task_ref_ids,
            filter_email_task_ref_ids=filter_email_task_ref_ids,
        )

        gen_log_entry.additional_properties = d
        return gen_log_entry

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
