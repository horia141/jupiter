"""Repository for recurring tasks."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from typing import Final, Any, ClassVar, Dict, Iterable, List, Optional

from models.basic import EntityId, Eisen, Difficulty, RecurringTaskPeriod, EntityName
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage

LOGGER = logging.getLogger(__name__)


@dataclass()
class RecurringTask:
    """A recurring task."""

    ref_id: EntityId
    project_ref_id: EntityId
    archived: bool
    name: str
    period: RecurringTaskPeriod
    group: EntityName
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    suspended: bool
    skip_rule: Optional[str]
    must_do: bool


@typing.final
class RecurringTasksRepository:
    """A repository for recurring tasks."""

    _RECURRING_TASKS_FILE_PATH: ClassVar[Path] = Path("/data/recurring-tasks.yaml")

    _structured_storage: Final[StructuredCollectionStorage[RecurringTask]]

    def __init__(self) -> None:
        """Constructor."""
        self._structured_storage = StructuredCollectionStorage(self._RECURRING_TASKS_FILE_PATH, self)

    def __enter__(self) -> 'RecurringTasksRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_recurring_task(
            self, project_ref_id: EntityId, archived: bool, name: str, period: RecurringTaskPeriod,
            group: EntityName, eisen: Iterable[Eisen], difficulty: Optional[Difficulty],
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
            group=group,
            eisen=list(eisen),
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            suspended=suspended,
            skip_rule=skip_rule,
            must_do=must_do)

        recurring_tasks_next_idx += 1
        recurring_tasks.append(new_recurring_task)

        self._structured_storage.save((recurring_tasks_next_idx, recurring_tasks))

        return new_recurring_task

    def remove_recurring_task_by_id(self, ref_id: EntityId) -> RecurringTask:
        """Remove a particular recurring task."""
        recurring_tasks_next_idx, recurring_tasks = self._structured_storage.load()

        for recurring_task in recurring_tasks:
            if recurring_task.ref_id == ref_id:
                recurring_task.archived = True
                self._structured_storage.save((recurring_tasks_next_idx, recurring_tasks))
                return recurring_task

        raise RepositoryError(f"Recurring task with id='{ref_id}' does not exist")

    def list_all_recurring_tasks(
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

    def load_recurring_task_by_id(self, ref_id: EntityId) -> RecurringTask:
        """Retrieve a particular recurring task by its id."""
        _, recurring_tasks = self._structured_storage.load()
        found_recurring_tasks = self._find_recurring_task_by_id(ref_id, recurring_tasks)
        if not found_recurring_tasks:
            raise RepositoryError(f"Recurring task with id='{ref_id}' does not exist")
        if found_recurring_tasks.archived:
            raise RepositoryError(f"Recurring task with id='{ref_id}' is archived")
        return found_recurring_tasks

    def save_recurring_task(self, new_recurring_task: RecurringTask) -> None:
        """Store a particular recurring task with all new properties."""
        recurring_tasks_next_idx, recurring_tasks = self._structured_storage.load()

        if not self._find_recurring_task_by_id(new_recurring_task.ref_id, recurring_tasks):
            raise RepositoryError(f"Recurring task with id='{new_recurring_task.ref_id}' does not exist")

        new_recurring_tasks = [(rt if rt.ref_id != new_recurring_task.ref_id else new_recurring_task)
                               for rt in recurring_tasks]
        self._structured_storage.save((recurring_tasks_next_idx, new_recurring_tasks))

    @staticmethod
    def _find_recurring_task_by_id(ref_id: EntityId, recurring_tasks: List[RecurringTask]) -> Optional[RecurringTask]:
        try:
            return next(rt for rt in recurring_tasks if rt.ref_id == ref_id)
        except StopIteration:
            return None

    @staticmethod
    def storage_schema() -> Dict[str, Any]:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "project_ref_id": {"type": "string"},
                "archived": {"type": "boolean"},
                "name": {"type": "string"},
                "period": {"type": "string"},
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
                "must_do": {"type": "boolean"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: Any) -> RecurringTask:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return RecurringTask(
            ref_id=EntityId(storage_form["ref_id"]),
            project_ref_id=EntityId(storage_form["project_ref_id"]),
            archived=storage_form.get("archived", False),
            name=storage_form["name"],
            period=RecurringTaskPeriod(storage_form["period"]),
            group=EntityName(storage_form["group"]),
            eisen=[Eisen(e) for e in storage_form["eisen"]],
            difficulty=Difficulty(storage_form["difficulty"]) if storage_form["difficulty"] else None,
            due_at_time=storage_form["due_at_time"] if storage_form["due_at_time"] else None,
            due_at_day=storage_form["due_at_day"] if storage_form["due_at_day"] else None,
            due_at_month=storage_form["due_at_month"] if storage_form["due_at_month"] else None,
            suspended=storage_form["suspended"],
            skip_rule=storage_form["skip_rule"] if storage_form["skip_rule"] else None,
            must_do=storage_form["must_do"])

    @staticmethod
    def live_to_storage(live_form: RecurringTask) -> Any:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "project_ref_id": live_form.project_ref_id,
            "archived": live_form.archived,
            "name": live_form.name,
            "period": live_form.period.value,
            "group": live_form.group,
            "eisen": [e.value for e in live_form.eisen],
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "due_at_time": live_form.due_at_time,
            "due_at_day": live_form.due_at_day,
            "due_at_month": live_form.due_at_month,
            "suspended": live_form.suspended,
            "skip_rule": live_form.skip_rule,
            "must_do": live_form.must_do
        }
