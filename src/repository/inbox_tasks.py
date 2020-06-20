"""Repository for inbox tasks."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, List, Optional

import pendulum

from models.basic import EntityId, Eisen, Difficulty, InboxTaskStatus
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage, JSONDictType
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class InboxTask:
    """An inbox task."""

    ref_id: EntityId
    project_ref_id: EntityId
    big_plan_ref_id: Optional[EntityId]
    recurring_task_ref_id: Optional[EntityId]
    name: str
    archived: bool
    status: InboxTaskStatus
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    due_date: Optional[pendulum.DateTime]
    recurring_task_timeline: Optional[str]
    created_time: pendulum.DateTime
    last_modified_time: pendulum.DateTime
    archived_time: Optional[pendulum.DateTime]
    accepted_time: Optional[pendulum.DateTime]
    working_time: Optional[pendulum.DateTime]
    completed_time: Optional[pendulum.DateTime]


@typing.final
class InboxTasksRepository:
    """A repository of the inbox tasks."""

    _INBOX_TASKS_FILE_PATH: ClassVar[Path] = Path("/data/inbox-tasks.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredCollectionStorage[InboxTask]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredCollectionStorage(self._INBOX_TASKS_FILE_PATH, self)

    def __enter__(self) -> 'InboxTasksRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_inbox_task(
            self, project_ref_id: EntityId, big_plan_ref_id: Optional[EntityId],
            recurring_task_ref_id: Optional[EntityId], name: str, archived: bool, status: InboxTaskStatus,
            eisen: Iterable[Eisen], difficulty: Optional[Difficulty], due_date: Optional[pendulum.DateTime],
            recurring_task_timeline: Optional[str]) -> InboxTask:
        """Create a recurring task."""
        inbox_tasks_next_idx, inbox_tasks = self._structured_storage.load()

        new_inbox_task = InboxTask(
            ref_id=EntityId(str(inbox_tasks_next_idx)),
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            recurring_task_ref_id=recurring_task_ref_id,
            name=name,
            archived=archived,
            status=status,
            eisen=list(eisen),
            difficulty=difficulty,
            due_date=due_date,
            recurring_task_timeline=recurring_task_timeline,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time(),
            archived_time=self._time_provider.get_current_time() if archived else None,
            accepted_time=self._time_provider.get_current_time() if status.is_accepted_or_more else None,
            working_time=self._time_provider.get_current_time() if status.is_working_or_more else None,
            completed_time=self._time_provider.get_current_time() if status.is_completed else None)

        inbox_tasks_next_idx += 1
        inbox_tasks.append(new_inbox_task)

        self._structured_storage.save((inbox_tasks_next_idx, inbox_tasks))

        return new_inbox_task

    def archive_inbox_task(self, ref_id: EntityId) -> InboxTask:
        """Remove a particular inbox task."""
        inbox_tasks_next_idx, inbox_tasks = self._structured_storage.load()

        for inbox_task in inbox_tasks:
            if inbox_task.ref_id == ref_id:
                inbox_task.archived = True
                inbox_task.last_modified_time = self._time_provider.get_current_time()
                inbox_task.archived_time = self._time_provider.get_current_time()
                self._structured_storage.save((inbox_tasks_next_idx, inbox_tasks))
                return inbox_task

        raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")

    def load_all_inbox_task(
            self,
            filter_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTask]:
        """Retrieve all the inbox tasks defined."""
        _, inbox_tasks = self._structured_storage.load()
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else []
        filter_project_ref_ids_set = frozenset(filter_project_ref_ids) if filter_project_ref_ids else []
        filter_big_plan_ref_ids_set = frozenset(filter_big_plan_ref_ids) if filter_big_plan_ref_ids else []
        filter_recurring_task_ref_ids_set = frozenset(filter_recurring_task_ref_ids)\
            if filter_recurring_task_ref_ids else []
        return [it for it in inbox_tasks
                if (filter_archived is False or it.archived is False)
                and (len(filter_ref_ids_set) == 0 or it.ref_id in filter_ref_ids_set)
                and (len(filter_project_ref_ids_set) == 0 or it.project_ref_id in filter_project_ref_ids_set)
                and (len(filter_big_plan_ref_ids_set) == 0 or it.big_plan_ref_id in filter_big_plan_ref_ids_set)
                and (len(filter_recurring_task_ref_ids_set) == 0
                     or it.recurring_task_ref_id in filter_recurring_task_ref_ids_set)]

    def load_inbox_task(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTask:
        """Retrieve a particular inbox task by its id."""
        _, inbox_tasks = self._structured_storage.load()
        found_inbox_task = self._find_inbox_task_by_id(ref_id, inbox_tasks)
        if not found_inbox_task:
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")
        if not allow_archived and found_inbox_task.archived:
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")
        return found_inbox_task

    def save_inbox_task(
            self, new_inbox_task: InboxTask,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            accepted_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            working_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            completed_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> InboxTask:
        """Store a particular inbox task with all new properties."""
        inbox_tasks_next_idx, inbox_tasks = self._structured_storage.load()

        if not self._find_inbox_task_by_id(new_inbox_task.ref_id, inbox_tasks):
            raise RepositoryError(f"Inbox task with id='{new_inbox_task.ref_id}' does not exist")

        new_inbox_task.last_modified_time = self._time_provider.get_current_time()
        archived_time_action.act(new_inbox_task, "archived_time", self._time_provider.get_current_time())
        accepted_time_action.act(new_inbox_task, "accepted_time", self._time_provider.get_current_time())
        working_time_action.act(new_inbox_task, "working_time", self._time_provider.get_current_time())
        completed_time_action.act(new_inbox_task, "completed_time", self._time_provider.get_current_time())
        new_inbox_tasks = [(rt if rt.ref_id != new_inbox_task.ref_id else new_inbox_task)
                           for rt in inbox_tasks]
        self._structured_storage.save((inbox_tasks_next_idx, new_inbox_tasks))

        return new_inbox_task

    def hard_remove_inbox_task(self, ref_id: EntityId) -> InboxTask:
        """Hard remove an inbox task."""
        inbox_tasks_next_idx, inbox_tasks = self._structured_storage.load()
        found_inbox_task = self._find_inbox_task_by_id(ref_id, inbox_tasks)
        if not found_inbox_task:
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")
        new_inbox_tasks = [it for it in inbox_tasks if it.ref_id != ref_id]
        self._structured_storage.save((inbox_tasks_next_idx, new_inbox_tasks))
        return found_inbox_task

    @staticmethod
    def _find_inbox_task_by_id(ref_id: EntityId, inbox_tasks: List[InboxTask]) -> Optional[InboxTask]:
        try:
            return next(it for it in inbox_tasks if it.ref_id == ref_id)
        except StopIteration:
            return None

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
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
                "due_date": {"type": ["string", "null"]},
                "recurring_task_timeline": {"type": ["string", "null"]},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"},
                "archived_time": {"type": ["string", "null"]},
                "accepted_time": {"type": ["string", "null"]},
                "working_time": {"type": ["string", "null"]},
                "completed_time": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> InboxTask:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return InboxTask(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
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
            due_date=pendulum.parse(typing.cast(str, storage_form["due_date"]))
            if storage_form["due_date"] else None,
            recurring_task_timeline=typing.cast(str, storage_form["recurring_task_timeline"])
            if storage_form["recurring_task_timeline"] else None,
            created_time=pendulum.parse(typing.cast(str, storage_form["created_time"])),
            last_modified_time=pendulum.parse(typing.cast(str, storage_form["last_modified_time"])),
            archived_time=pendulum.parse(typing.cast(str, storage_form["archived_time"]))
            if storage_form["archived_time"] else None,
            accepted_time=pendulum.parse(typing.cast(str, storage_form["accepted_time"]))
            if storage_form["accepted_time"] else None,
            working_time=pendulum.parse(typing.cast(str, storage_form["working_time"]))
            if storage_form["working_time"] else None,
            completed_time=pendulum.parse(typing.cast(str, storage_form["completed_time"]))
            if storage_form["completed_time"] else None)

    @staticmethod
    def live_to_storage(live_form: InboxTask) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "project_ref_id": live_form.project_ref_id,
            "big_plan_ref_id": live_form.big_plan_ref_id,
            "recurring_task_ref_id": live_form.recurring_task_ref_id,
            "name": live_form.name,
            "archived": live_form.archived,
            "status": live_form.status.value,
            "eisen": [e.value for e in live_form.eisen],
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "due_date": live_form.due_date.to_datetime_string() if live_form.due_date else None,
            "recurring_task_timeline": live_form.recurring_task_timeline,
            "created_time": live_form.created_time.to_datetime_string(),
            "last_modified_time": live_form.last_modified_time.to_datetime_string(),
            "archived_time": live_form.archived_time.to_datetime_string() if live_form.archived_time else None,
            "accepted_time": live_form.accepted_time.to_datetime_string() if live_form.accepted_time else None,
            "working_time": live_form.working_time.to_datetime_string() if live_form.working_time else None,
            "completed_time": live_form.completed_time.to_datetime_string() if live_form.completed_time else None
        }
