"""Repository for inbox tasks."""

import logging
import typing
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, List, Optional

from domain.common.adate import ADate
from domain.common.difficulty import Difficulty
from domain.common.eisen import Eisen
from domain.common.entity_name import EntityName
from domain.common.recurring_task_type import RecurringTaskType
from domain.common.timestamp import Timestamp
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from models.framework import EntityId, JSONDictType
from utils.storage import BaseEntityRow, EntitiesStorage, In
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class InboxTaskRow(BaseEntityRow):
    """An inbox task."""

    project_ref_id: EntityId
    source: InboxTaskSource
    big_plan_ref_id: Optional[EntityId]
    recurring_task_ref_id: Optional[EntityId]
    metric_ref_id: Optional[EntityId]
    person_ref_id: Optional[EntityId]
    name: EntityName
    archived: bool
    status: InboxTaskStatus
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    recurring_timeline: Optional[str]
    recurring_type: Optional[RecurringTaskType]
    recurring_gen_right_now: Optional[Timestamp]  # Time for which this inbox task was generated
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


class InboxTasksRepository:
    """A repository of the inbox tasks."""

    _INBOX_TASKS_FILE_PATH: ClassVar[Path] = Path("./inbox-tasks")
    _INBOX_TASKS_NUM_SHARDS: ClassVar[int] = 50

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[InboxTaskRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[InboxTaskRow](
            self._INBOX_TASKS_FILE_PATH, self._INBOX_TASKS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'InboxTasksRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_inbox_task(
            self, project_ref_id: EntityId, source: InboxTaskSource, big_plan_ref_id: Optional[EntityId],
            recurring_task_ref_id: Optional[EntityId], metric_ref_id: Optional[EntityId],
            person_ref_id: Optional[EntityId], name: EntityName, archived: bool, status: InboxTaskStatus,
            eisen: Iterable[Eisen], difficulty: Optional[Difficulty], actionable_date: Optional[ADate],
            due_date: Optional[ADate], recurring_timeline: Optional[str], recurring_type: Optional[RecurringTaskType],
            recurring_gen_right_now: Optional[Timestamp]) -> InboxTaskRow:
        """Create a recurring task."""
        new_inbox_task_row = InboxTaskRow(
            project_ref_id=project_ref_id,
            source=source,
            big_plan_ref_id=big_plan_ref_id,
            recurring_task_ref_id=recurring_task_ref_id,
            metric_ref_id=metric_ref_id,
            person_ref_id=person_ref_id,
            name=name,
            archived=archived,
            status=status,
            eisen=list(eisen),
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_timeline=recurring_timeline,
            recurring_type=recurring_type,
            recurring_gen_right_now=recurring_gen_right_now,
            accepted_time=self._time_provider.get_current_time() if status.is_accepted_or_more else None,
            working_time=self._time_provider.get_current_time() if status.is_working_or_more else None,
            completed_time=self._time_provider.get_current_time() if status.is_completed else None)

        return self._storage.create(new_inbox_task_row)

    def archive_inbox_task(self, ref_id: EntityId) -> InboxTaskRow:
        """Remove a particular inbox task."""
        return self._storage.archive(ref_id)

    def remove_inbox_task(self, ref_id: EntityId) -> InboxTaskRow:
        """Hard remove an inbox task."""
        return self._storage.remove(ref_id)

    def update_inbox_task(
            self, new_inbox_task_row: InboxTaskRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            accepted_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            working_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            completed_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> InboxTaskRow:
        """Store a particular inbox task with all new properties."""
        accepted_time_action.act(new_inbox_task_row, "accepted_time", self._time_provider.get_current_time())
        working_time_action.act(new_inbox_task_row, "working_time", self._time_provider.get_current_time())
        completed_time_action.act(new_inbox_task_row, "completed_time", self._time_provider.get_current_time())
        return self._storage.update(new_inbox_task_row, archived_time_action=archived_time_action)

    def save_all(self, all_inbox_tasks: Iterable[InboxTaskRow]) -> None:
        """Save all given inbox tasks and overwrite old ones."""
        self._storage.dump_all(all_inbox_tasks)

    def load_inbox_task(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTaskRow:
        """Retrieve a particular inbox task by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_inbox_tasks(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_sources: Optional[Iterable[InboxTaskSource]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_person_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTaskRow]:
        """Retrieve all the inbox tasks defined."""
        return self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(*filter_project_ref_ids) if filter_project_ref_ids else None,
            source=In(*filter_sources) if filter_sources else None,
            big_plan_ref_id=In(*filter_big_plan_ref_ids) if filter_big_plan_ref_ids else None,
            recurring_task_ref_id=In(*filter_recurring_task_ref_ids) if filter_recurring_task_ref_ids else None,
            metric_ref_id=In(*filter_metric_ref_ids) if filter_metric_ref_ids else None,
            person_ref_id=In(*filter_person_ref_ids) if filter_person_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"},
            "source": {"type": ["string", "null"]},
            "big_plan_ref_id": {"type": ["string", "null"]},
            "recurring_tasks_ref_id": {"type": ["string", "null"]},
            "metric_ref_id": {"type": ["string", "null"]},
            "person_ref_id": {"type": ["string", "null"]},
            "name": {"type": "string"},
            "archived": {"type": "boolean"},
            "eisen": {
                "type": "array",
                "entries": {"type": "string"}
            },
            "difficulty": {"type": ["string", "null"]},
            "actionable_date": {"type": ["string", "null"]},
            "due_date": {"type": ["string", "null"]},
            "recurring_timeline": {"type": ["string", "null"]},
            "recurring_type": {"type": ["string", "null"]},
            "recurring_gen_right_now": {"type": ["string", "null"]},
            "recurring_task_timeline": {"type": ["string", "null"]},
            "recurring_task_type": {"type": ["string", "null"]},
            "recurring_task_gen_right_now": {"type": ["string", "null"]},
            "accepted_time": {"type": ["string", "null"]},
            "working_time": {"type": ["string", "null"]},
            "completed_time": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> InboxTaskRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return InboxTaskRow(
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            source=InboxTaskSource.from_raw(typing.cast(str, storage_form["source"])),
            big_plan_ref_id=EntityId(typing.cast(str, storage_form["big_plan_ref_id"]))
            if storage_form["big_plan_ref_id"] else None,
            recurring_task_ref_id=EntityId(typing.cast(str, (storage_form["recurring_task_ref_id"])))
            if storage_form["recurring_task_ref_id"] else None,
            metric_ref_id=EntityId(typing.cast(str, storage_form["metric_ref_id"]))
            if storage_form["metric_ref_id"] else None,
            person_ref_id=EntityId(typing.cast(str, storage_form["person_ref_id"]))
            if storage_form.get("person_ref_id", None) else None,
            name=EntityName.from_raw(typing.cast(str, storage_form["name"])),
            archived=typing.cast(bool, storage_form["archived"]),
            status=InboxTaskStatus(typing.cast(str, storage_form["status"])),
            eisen=[Eisen(e) for e in typing.cast(List[str], storage_form["eisen"])],
            difficulty=Difficulty(typing.cast(str, storage_form["difficulty"]))
            if storage_form["difficulty"] else None,
            actionable_date=ADate.from_str(typing.cast(str, storage_form["actionable_date"]))
            if storage_form["actionable_date"] else None,
            due_date=ADate.from_str(typing.cast(str, storage_form["due_date"]))
            if storage_form["due_date"] else None,
            recurring_timeline=typing.cast(str, storage_form["recurring_timeline"])
            if storage_form["recurring_timeline"] else None,
            recurring_type=RecurringTaskType(typing.cast(str, storage_form["recurring_type"]))
            if storage_form["recurring_type"] else None,
            recurring_gen_right_now=Timestamp.from_str(
                typing.cast(str, storage_form["recurring_gen_right_now"]))
            if storage_form["recurring_gen_right_now"] else None,
            accepted_time=Timestamp.from_str(typing.cast(str, storage_form["accepted_time"]))
            if storage_form["accepted_time"] else None,
            working_time=Timestamp.from_str(typing.cast(str, storage_form["working_time"]))
            if storage_form["working_time"] else None,
            completed_time=Timestamp.from_str(typing.cast(str, storage_form["completed_time"]))
            if storage_form["completed_time"] else None)

    @staticmethod
    def live_to_storage(live_form: InboxTaskRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": str(live_form.project_ref_id),
            "source": live_form.source.value,
            "big_plan_ref_id": str(live_form.big_plan_ref_id) if live_form.big_plan_ref_id else None,
            "recurring_task_ref_id": str(live_form.recurring_task_ref_id) if live_form.recurring_task_ref_id else None,
            "metric_ref_id": str(live_form.metric_ref_id) if live_form.metric_ref_id else None,
            "person_ref_id": str(live_form.person_ref_id) if live_form.person_ref_id else None,
            "name": str(live_form.name),
            "status": live_form.status.value,
            "eisen": [e.value for e in live_form.eisen],
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "actionable_date": str(live_form.actionable_date)
                               if live_form.actionable_date else None,
            "due_date": str(live_form.due_date) if live_form.due_date else None,
            "recurring_timeline": live_form.recurring_timeline,
            "recurring_type": live_form.recurring_type.value if live_form.recurring_type else None,
            "recurring_gen_right_now": str(live_form.recurring_gen_right_now)
                                       if live_form.recurring_gen_right_now else None,
            "accepted_time": str(live_form.accepted_time)
                             if live_form.accepted_time else None,
            "working_time": str(live_form.working_time)
                            if live_form.working_time else None,
            "completed_time": str(live_form.completed_time)
                              if live_form.completed_time else None
        }
