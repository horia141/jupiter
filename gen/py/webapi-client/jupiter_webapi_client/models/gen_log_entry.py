from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

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
        gen_log (str):
        source (EventSource): The source of the modification which this event records.
        gen_even_if_not_modified (bool):
        today (str): A date or possibly a datetime for the application.
        gen_targets (List[SyncTarget]):
        opened (bool):
        entity_created_records (List['EntitySummary']):
        entity_updated_records (List['EntitySummary']):
        entity_removed_records (List['EntitySummary']):
        archived_time (Union[Unset, str]): A timestamp in the application.
        period (Union[Unset, List[RecurringTaskPeriod]]):
        filter_project_ref_ids (Union[Unset, List[str]]):
        filter_habit_ref_ids (Union[Unset, List[str]]):
        filter_chore_ref_ids (Union[Unset, List[str]]):
        filter_metric_ref_ids (Union[Unset, List[str]]):
        filter_person_ref_ids (Union[Unset, List[str]]):
        filter_slack_task_ref_ids (Union[Unset, List[str]]):
        filter_email_task_ref_ids (Union[Unset, List[str]]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    gen_log: str
    source: EventSource
    gen_even_if_not_modified: bool
    today: str
    gen_targets: List[SyncTarget]
    opened: bool
    entity_created_records: List["EntitySummary"]
    entity_updated_records: List["EntitySummary"]
    entity_removed_records: List["EntitySummary"]
    archived_time: Union[Unset, str] = UNSET
    period: Union[Unset, List[RecurringTaskPeriod]] = UNSET
    filter_project_ref_ids: Union[Unset, List[str]] = UNSET
    filter_habit_ref_ids: Union[Unset, List[str]] = UNSET
    filter_chore_ref_ids: Union[Unset, List[str]] = UNSET
    filter_metric_ref_ids: Union[Unset, List[str]] = UNSET
    filter_person_ref_ids: Union[Unset, List[str]] = UNSET
    filter_slack_task_ref_ids: Union[Unset, List[str]] = UNSET
    filter_email_task_ref_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        gen_log = self.gen_log

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

        archived_time = self.archived_time

        period: Union[Unset, List[str]] = UNSET
        if not isinstance(self.period, Unset):
            period = []
            for period_item_data in self.period:
                period_item = period_item_data.value
                period.append(period_item)

        filter_project_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_habit_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        filter_chore_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_chore_ref_ids, Unset):
            filter_chore_ref_ids = self.filter_chore_ref_ids

        filter_metric_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_metric_ref_ids, Unset):
            filter_metric_ref_ids = self.filter_metric_ref_ids

        filter_person_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_person_ref_ids, Unset):
            filter_person_ref_ids = self.filter_person_ref_ids

        filter_slack_task_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_slack_task_ref_ids, Unset):
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        filter_email_task_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_email_task_ref_ids, Unset):
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "gen_log": gen_log,
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entity_summary import EntitySummary

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        gen_log = d.pop("gen_log")

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

        archived_time = d.pop("archived_time", UNSET)

        period = []
        _period = d.pop("period", UNSET)
        for period_item_data in _period or []:
            period_item = RecurringTaskPeriod(period_item_data)

            period.append(period_item)

        filter_project_ref_ids = cast(List[str], d.pop("filter_project_ref_ids", UNSET))

        filter_habit_ref_ids = cast(List[str], d.pop("filter_habit_ref_ids", UNSET))

        filter_chore_ref_ids = cast(List[str], d.pop("filter_chore_ref_ids", UNSET))

        filter_metric_ref_ids = cast(List[str], d.pop("filter_metric_ref_ids", UNSET))

        filter_person_ref_ids = cast(List[str], d.pop("filter_person_ref_ids", UNSET))

        filter_slack_task_ref_ids = cast(List[str], d.pop("filter_slack_task_ref_ids", UNSET))

        filter_email_task_ref_ids = cast(List[str], d.pop("filter_email_task_ref_ids", UNSET))

        gen_log_entry = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            gen_log=gen_log,
            source=source,
            gen_even_if_not_modified=gen_even_if_not_modified,
            today=today,
            gen_targets=gen_targets,
            opened=opened,
            entity_created_records=entity_created_records,
            entity_updated_records=entity_updated_records,
            entity_removed_records=entity_removed_records,
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
