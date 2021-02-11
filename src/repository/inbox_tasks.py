"""Repository for inbox tasks."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, List, Optional

from models.basic import EntityId, Eisen, Difficulty, InboxTaskStatus, RecurringTaskType, ADate, BasicValidator, \
    Timestamp
from utils.storage import JSONDictType, BaseEntityRow, EntitiesStorage, In
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class InboxTaskRow(BaseEntityRow):
    """An inbox task."""

    project_ref_id: EntityId
    big_plan_ref_id: Optional[EntityId]
    recurring_task_ref_id: Optional[EntityId]
    name: str
    archived: bool
    status: InboxTaskStatus
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    recurring_task_timeline: Optional[str]
    recurring_task_type: Optional[RecurringTaskType]
    recurring_task_gen_right_now: Optional[Timestamp]  # Time for which this inbox task was generated
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


@typing.final
class InboxTasksRepository:
    """A repository of the inbox tasks."""

    _INBOX_TASKS_FILE_PATH: ClassVar[Path] = Path("./inbox-tasks.yaml")

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[InboxTaskRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[InboxTaskRow](self._INBOX_TASKS_FILE_PATH, time_provider, self)

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
            self, project_ref_id: EntityId, big_plan_ref_id: Optional[EntityId],
            recurring_task_ref_id: Optional[EntityId], name: str, archived: bool, status: InboxTaskStatus,
            eisen: Iterable[Eisen], difficulty: Optional[Difficulty], actionable_date: Optional[ADate],
            due_date: Optional[ADate], recurring_task_timeline: Optional[str],
            recurring_task_type: Optional[RecurringTaskType],
            recurring_task_gen_right_now: Optional[Timestamp]) -> InboxTaskRow:
        """Create a recurring task."""
        new_inbox_task_row = InboxTaskRow(
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            recurring_task_ref_id=recurring_task_ref_id,
            name=name,
            archived=archived,
            status=status,
            eisen=list(eisen),
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_task_timeline=recurring_task_timeline,
            recurring_task_type=recurring_task_type,
            recurring_task_gen_right_now=recurring_task_gen_right_now,
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

    def load_inbox_task(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTaskRow:
        """Retrieve a particular inbox task by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_inbox_tasks(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTaskRow]:
        """Retrieve all the inbox tasks defined."""
        return self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(*filter_project_ref_ids) if filter_project_ref_ids else None,
            big_plan_ref_id=In(*filter_big_plan_ref_ids) if filter_big_plan_ref_ids else None,
            recurring_task_ref_id=In(*filter_recurring_task_ref_ids) if filter_recurring_task_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"},
            "big_plan_ref_id": {"type": ["string", "null"]},
            "recurring_tasks_ref_id": {"type": ["string", "null"]},
            "name": {"type": "string"},
            "archived": {"type": "boolean"},
            "eisen": {
                "type": "array",
                "entries": {"type": "string"}
            },
            "difficulty": {"type": ["string", "null"]},
            "actionable_date": {"type": ["string", "null"]},
            "due_date": {"type": ["string", "null"]},
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
            big_plan_ref_id=EntityId(typing.cast(str, storage_form["big_plan_ref_id"]))
            if storage_form["big_plan_ref_id"] else None,
            recurring_task_ref_id=EntityId(typing.cast(str, (storage_form["recurring_task_ref_id"])))
            if storage_form["recurring_task_ref_id"] else None,
            name=typing.cast(str, storage_form["name"]),
            archived=typing.cast(bool, storage_form["archived"]),
            status=InboxTaskStatus(typing.cast(str, storage_form["status"])),
            eisen=[Eisen(e) for e in typing.cast(List[str], storage_form["eisen"])],
            difficulty=Difficulty(typing.cast(str, storage_form["difficulty"]))
            if storage_form["difficulty"] else None,
            actionable_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["actionable_date"]))
            if storage_form["actionable_date"] else None,
            due_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["due_date"]))
            if storage_form["due_date"] else None,
            recurring_task_timeline=typing.cast(str, storage_form["recurring_task_timeline"])
            if storage_form["recurring_task_timeline"] else None,
            recurring_task_type=RecurringTaskType(typing.cast(str, storage_form["recurring_task_type"]))
            if storage_form["recurring_task_type"] else None,
            recurring_task_gen_right_now=BasicValidator.timestamp_from_str(
                typing.cast(str, storage_form["recurring_task_gen_right_now"]))
            if storage_form["recurring_task_gen_right_now"] else None,
            accepted_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["accepted_time"]))
            if storage_form["accepted_time"] else None,
            working_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["working_time"]))
            if storage_form["working_time"] else None,
            completed_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["completed_time"]))
            if storage_form["completed_time"] else None)

    @staticmethod
    def live_to_storage(live_form: InboxTaskRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": live_form.project_ref_id,
            "big_plan_ref_id": live_form.big_plan_ref_id,
            "recurring_task_ref_id": live_form.recurring_task_ref_id,
            "name": live_form.name,
            "status": live_form.status.value,
            "eisen": [e.value for e in live_form.eisen],
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "actionable_date": BasicValidator.adate_to_str(live_form.actionable_date)
                               if live_form.actionable_date else None,
            "due_date": BasicValidator.adate_to_str(live_form.due_date) if live_form.due_date else None,
            "recurring_task_timeline": live_form.recurring_task_timeline,
            "recurring_task_type": live_form.recurring_task_type.value if live_form.recurring_task_type else None,
            "recurring_task_gen_right_now": BasicValidator.timestamp_to_str(live_form.recurring_task_gen_right_now)
                                            if live_form.recurring_task_gen_right_now else None,
            "accepted_time": BasicValidator.timestamp_to_str(live_form.accepted_time)
                             if live_form.accepted_time else None,
            "working_time": BasicValidator.timestamp_to_str(live_form.working_time)
                            if live_form.working_time else None,
            "completed_time": BasicValidator.timestamp_to_str(live_form.completed_time)
                              if live_form.completed_time else None
        }
