"""Repository for recurring tasks."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, List, Optional

from models.basic import EntityId, Eisen, Difficulty, RecurringTaskPeriod, EntityName, RecurringTaskType, Timestamp, \
    BasicValidator
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage, JSONDictType
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class RecurringTask:
    """A recurring task."""

    ref_id: EntityId
    project_ref_id: EntityId
    archived: bool
    name: str
    period: RecurringTaskPeriod
    the_type: RecurringTaskType
    group: EntityName
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    suspended: bool
    skip_rule: Optional[str]
    must_do: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]


@typing.final
class RecurringTasksRepository:
    """A repository for recurring tasks."""

    _RECURRING_TASKS_FILE_PATH: ClassVar[Path] = Path("/data/recurring-tasks.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredCollectionStorage[RecurringTask]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredCollectionStorage(self._RECURRING_TASKS_FILE_PATH, self)

    def __enter__(self) -> 'RecurringTasksRepository':
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

    def create_recurring_task(
            self, project_ref_id: EntityId, archived: bool, name: str, period: RecurringTaskPeriod,
            the_type: RecurringTaskType, group: EntityName, eisen: Iterable[Eisen], difficulty: Optional[Difficulty],
            due_at_time: Optional[str], due_at_day: Optional[int], due_at_month: Optional[int], suspended: bool,
            skip_rule: Optional[str], must_do: bool) -> RecurringTask:
        """Create a recurring task."""
        recurring_tasks_next_idx, recurring_tasks = self._structured_storage.load()

        new_recurring_task = RecurringTask(
            ref_id=EntityId(str(recurring_tasks_next_idx)),
            project_ref_id=project_ref_id,
            archived=archived,
            name=name,
            period=period,
            the_type=the_type,
            group=group,
            eisen=list(eisen),
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            suspended=suspended,
            skip_rule=skip_rule,
            must_do=must_do,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time(),
            archived_time=self._time_provider.get_current_time() if archived else None)

        recurring_tasks_next_idx += 1
        recurring_tasks.append(new_recurring_task)

        self._structured_storage.save((recurring_tasks_next_idx, recurring_tasks))

        return new_recurring_task

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Remove a particular recurring task."""
        recurring_tasks_next_idx, recurring_tasks = self._structured_storage.load()

        for recurring_task in recurring_tasks:
            if recurring_task.ref_id == ref_id:
                recurring_task.archived = True
                recurring_task.last_modified_time = self._time_provider.get_current_time()
                recurring_task.archived_time = self._time_provider.get_current_time()
                self._structured_storage.save((recurring_tasks_next_idx, recurring_tasks))
                return recurring_task

        raise RepositoryError(f"Recurring task with id='{ref_id}' does not exist")

    def load_all_recurring_tasks(
            self,
            filter_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTask]:
        """Retrieve all the recurring tasks defined."""
        _, recurring_tasks = self._structured_storage.load()
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else []
        filter_project_ref_ids_set = frozenset(filter_project_ref_ids) if filter_project_ref_ids else []
        return [r for r in recurring_tasks
                if (filter_archived is False or r.archived is False)
                and (len(filter_ref_ids_set) == 0 or r.ref_id in filter_ref_ids_set)
                and (len(filter_project_ref_ids_set) == 0 or r.project_ref_id in filter_project_ref_ids_set)]

    def load_recurring_task(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTask:
        """Retrieve a particular recurring task by its id."""
        _, recurring_tasks = self._structured_storage.load()
        found_recurring_tasks = self._find_recurring_task_by_id(ref_id, recurring_tasks)
        if not found_recurring_tasks:
            raise RepositoryError(f"Recurring task with id='{ref_id}' does not exist")
        if not allow_archived and found_recurring_tasks.archived:
            raise RepositoryError(f"Recurring task with id='{ref_id}' is archived")
        return found_recurring_tasks

    def save_recurring_task(
            self, new_recurring_task: RecurringTask,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> RecurringTask:
        """Store a particular recurring task with all new properties."""
        recurring_tasks_next_idx, recurring_tasks = self._structured_storage.load()

        if not self._find_recurring_task_by_id(new_recurring_task.ref_id, recurring_tasks):
            raise RepositoryError(f"Recurring task with id='{new_recurring_task.ref_id}' does not exist")

        new_recurring_task.last_modified_time = self._time_provider.get_current_time()
        archived_time_action.act(new_recurring_task, "archived_task", self._time_provider.get_current_time())
        new_recurring_tasks = [(rt if rt.ref_id != new_recurring_task.ref_id else new_recurring_task)
                               for rt in recurring_tasks]
        self._structured_storage.save((recurring_tasks_next_idx, new_recurring_tasks))

        return new_recurring_task

    def hard_remove_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Hard remove an inbox task."""
        recurring_tasks_next_idx, recurring_tasks = self._structured_storage.load()
        found_recurring_task = self._find_recurring_task_by_id(ref_id, recurring_tasks)
        if not found_recurring_task:
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")
        new_recurring_tasks = [it for it in recurring_tasks if it.ref_id != ref_id]
        self._structured_storage.save((recurring_tasks_next_idx, new_recurring_tasks))
        return found_recurring_task

    @staticmethod
    def _find_recurring_task_by_id(ref_id: EntityId, recurring_tasks: List[RecurringTask]) -> Optional[RecurringTask]:
        try:
            return next(rt for rt in recurring_tasks if rt.ref_id == ref_id)
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
                "archived": {"type": "boolean"},
                "name": {"type": "string"},
                "period": {"type": "string"},
                "the_type": {"type": "string"},
                "group": {"type": "string"},
                "eisen": {
                    "type": "array",
                    "entries": {"type": "string"}
                },
                "difficulty": {"type": ["string", "null"]},
                "due_at_time": {"type": ["string", "null"]},
                "due_at_day": {"type": ["number", "null"]},
                "due_at_month": {"type": ["number", "null"]},
                "suspended": {"type": "boolean"},
                "skip_rule": {"type": ["string", "null"]},
                "must_do": {"type": "boolean"},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"},
                "archived_time": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> RecurringTask:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return RecurringTask(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=typing.cast(str, storage_form["name"]),
            period=RecurringTaskPeriod(typing.cast(str, storage_form["period"])),
            the_type=RecurringTaskType(typing.cast(str, storage_form["the_type"])),
            group=EntityName(typing.cast(str, storage_form["group"])),
            eisen=[Eisen(e) for e in typing.cast(List[str], storage_form["eisen"])],
            difficulty=Difficulty(typing.cast(str, storage_form["difficulty"])) if storage_form["difficulty"] else None,
            due_at_time=typing.cast(str, storage_form["due_at_time"]) if storage_form["due_at_time"] else None,
            due_at_day=typing.cast(int, storage_form["due_at_day"]) if storage_form["due_at_day"] else None,
            due_at_month=typing.cast(int, storage_form["due_at_month"]) if storage_form["due_at_month"] else None,
            suspended=typing.cast(bool, storage_form["suspended"]),
            skip_rule=typing.cast(str, storage_form["skip_rule"]) if storage_form["skip_rule"] else None,
            must_do=typing.cast(bool, storage_form["must_do"]),
            created_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["last_modified_time"])),
            archived_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["archived_time"]))
            if storage_form["archived_time"] is not None else None)

    @staticmethod
    def live_to_storage(live_form: RecurringTask) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "project_ref_id": live_form.project_ref_id,
            "archived": live_form.archived,
            "name": live_form.name,
            "period": live_form.period.value,
            "the_type": live_form.the_type.value,
            "group": live_form.group,
            "eisen": [e.value for e in live_form.eisen],
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "due_at_time": live_form.due_at_time,
            "due_at_day": live_form.due_at_day,
            "due_at_month": live_form.due_at_month,
            "suspended": live_form.suspended,
            "skip_rule": live_form.skip_rule,
            "must_do": live_form.must_do,
            "created_time": BasicValidator.timestamp_to_str(live_form.created_time),
            "last_modified_time": BasicValidator.timestamp_to_str(live_form.last_modified_time),
            "archived_time": BasicValidator.timestamp_to_str(live_form.archived_time)
                             if live_form.archived_time else None
        }
