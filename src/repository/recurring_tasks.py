"""Repository for recurring tasks."""

from dataclasses import dataclass
import logging
import os.path
import typing
from typing import Final, Any, ClassVar, Dict, NewType, Iterable, List, Optional, Tuple, Set

import jsonschema as js
import yaml

from repository.common import RefId, RepositoryError, TaskPeriod, TaskEisen, TaskDifficulty

LOGGER = logging.getLogger(__name__)

RecurringTaskGroup = NewType("RecurringTaskGroup", str)


@typing.final
@dataclass()
class RecurringTask:
    """A recurring task."""

    ref_id: RefId
    project_ref_id: RefId
    archived: bool
    name: str
    period: TaskPeriod
    group: RecurringTaskGroup
    eisen: List[TaskEisen]
    difficulty: Optional[TaskDifficulty]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    suspended: bool
    skip_rule: Optional[str]
    must_do: bool


@typing.final
class RecurringTasksRepository:
    """A repository for recurring tasks."""

    _RECURRING_TASKS_FILE_PATH: ClassVar[str] = "/data/recurring-tasks.yaml"

    _RECURRING_TASKS_SCHEMA: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "next_idx": {"type": "number"},
            "entries": {
                "type": "array",
                "item": {
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
                        "difficulty": {"type": "string"},
                        "due_at_time": {"type": "string"},
                        "due_at_day": {"type": "number"},
                        "due_at_month": {"type": "number"},
                        "suspended": {"type": "boolean"},
                        "skip_rule": {"type": "string"},
                        "must_do": {"type": "boolean"}
                    }
                }
            }
        }
    }

    _validator: Final[Any]

    def __init__(self) -> None:
        """Constructor."""
        custom_type_checker = js.Draft6Validator.TYPE_CHECKER

        self._validator = js.validators.extend(js.Draft6Validator, type_checker=custom_type_checker)

    def initialize(self) -> None:
        """Initialise this repository."""
        if os.path.exists(RecurringTasksRepository._RECURRING_TASKS_FILE_PATH):
            return
        self._bulk_save_recurring_tasks((0, []))

    def create_recurring_task(
            self, project_ref_id: RefId, archived: bool, name: str, period: TaskPeriod, group: RecurringTaskGroup,
            eisen: Iterable[TaskEisen], difficulty: Optional[TaskDifficulty], due_at_time: Optional[str],
            due_at_day: Optional[int], due_at_month: Optional[int], suspended: bool, skip_rule: Optional[str],
            must_do: bool) -> RecurringTask:
        """Create a recurring task."""
        recurring_tasks_next_idx, recurring_tasks = self._bulk_load_recurring_tasks()

        new_recurring_task = RecurringTask(
            ref_id=RefId(str(recurring_tasks_next_idx)),
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

        self._bulk_save_recurring_tasks((recurring_tasks_next_idx, recurring_tasks))

        return new_recurring_task

    def remove_recurring_task_by_id(self, ref_id: RefId) -> None:
        """Remove a particular recurring task."""
        recurring_tasks_next_idx, recurring_tasks = self._bulk_load_recurring_tasks()

        for recurring_task in recurring_tasks:
            if recurring_task.ref_id == ref_id:
                recurring_task.archived = True
                break
        else:
            raise RepositoryError(f"Recurring task with id='{ref_id}' does not exist")

        self._bulk_save_recurring_tasks((recurring_tasks_next_idx, recurring_tasks))

    def list_all_recurring_tasks(
            self, filter_project_ref_id: Optional[Iterable[RefId]] = None) -> Iterable[RecurringTask]:
        """Retrieve all the recurring tasks defined."""
        _, recurring_tasks = self._bulk_load_recurring_tasks(
            filter_project_ref_id=frozenset(filter_project_ref_id) if filter_project_ref_id else None)
        return recurring_tasks

    def load_recurring_task_by_id(self, ref_id: RefId) -> RecurringTask:
        """Retrieve a particular recurring task by its id."""
        _, recurring_tasks = self._bulk_load_recurring_tasks()
        found_recurring_tasks = self._find_recurring_task_by_id(ref_id, recurring_tasks)
        if not found_recurring_tasks:
            raise RepositoryError(f"Recurring task with id='{ref_id}' does not exist")
        return found_recurring_tasks

    def save_recurring_task(self, new_recurring_task: RecurringTask) -> None:
        """Store a particular recurring task with all new properties."""
        recurring_tasks_next_idx, recurring_tasks = self._bulk_load_recurring_tasks()

        if not self._find_recurring_task_by_id(new_recurring_task.ref_id, recurring_tasks):
            raise RepositoryError(f"Recurring task with id='{new_recurring_task.ref_id}' does not exist")

        new_recurring_tasks = [(rt if rt.ref_id != new_recurring_task.ref_id else new_recurring_task)
                               for rt in recurring_tasks]
        self._bulk_save_recurring_tasks((recurring_tasks_next_idx, new_recurring_tasks))

    def _bulk_load_recurring_tasks(
            self, filter_project_ref_id: Optional[Set[RefId]] = None) -> Tuple[int, List[RecurringTask]]:
        try:
            with open(RecurringTasksRepository._RECURRING_TASKS_FILE_PATH, "r") as recurring_tasks_file:
                recurring_tasks_ser = yaml.safe_load(recurring_tasks_file)
                LOGGER.info("Loaded recurring tasks data")

                self._validator(RecurringTasksRepository._RECURRING_TASKS_SCHEMA).validate(recurring_tasks_ser)
                LOGGER.info("Checked recurring tasks structure")

                recurring_tasks_next_idx = recurring_tasks_ser["next_idx"]
                recurring_tasks_iter = \
                    (RecurringTask(
                        ref_id=RefId(rt["ref_id"]),
                        project_ref_id=RefId(rt["project_ref_id"]),
                        archived=rt.get("archived", False),
                        name=rt["name"],
                        period=TaskPeriod(rt["period"]),
                        group=RecurringTaskGroup(rt["group"]),
                        eisen=[TaskEisen(e) for e in rt["eisen"]],
                        difficulty=TaskDifficulty(rt["difficulty"]) if rt["difficulty"] else None,
                        due_at_time=rt["due_at_time"] if rt["due_at_time"] else None,
                        due_at_day=rt["due_at_day"] if rt["due_at_day"] else None,
                        due_at_month=rt["due_at_month"] if rt["due_at_month"] else None,
                        suspended=rt["suspended"],
                        skip_rule=rt["skip_rule"] if rt["skip_rule"] else None,
                        must_do=rt["must_do"])
                     for rt in recurring_tasks_ser["entries"])
                recurring_tasks = [rt for rt in recurring_tasks_iter
                                   if (rt.archived is False)
                                   and (filter_project_ref_id is None or rt.project_ref_id in filter_project_ref_id)]

                return recurring_tasks_next_idx, recurring_tasks
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    def _bulk_save_recurring_tasks(self, bulk_data: Tuple[int, List[RecurringTask]]) -> None:
        try:
            with open(RecurringTasksRepository._RECURRING_TASKS_FILE_PATH, "w") as recurring_tasks_file:
                recurring_tasks_ser = {
                    "next_idx": bulk_data[0],
                    "entries": [{
                        "ref_id": rt.ref_id,
                        "project_ref_id": rt.project_ref_id,
                        "archived": rt.archived,
                        "name": rt.name,
                        "period": rt.period.value,
                        "group": rt.group,
                        "eisen": [e.value for e in rt.eisen],
                        "difficulty": rt.difficulty.value if rt.difficulty else None,
                        "due_at_time": rt.due_at_time,
                        "due_at_day": rt.due_at_day,
                        "due_at_month": rt.due_at_month,
                        "suspended": rt.suspended,
                        "skip_rule": rt.skip_rule,
                        "must_do": rt.must_do
                    } for rt in bulk_data[1]]
                }

                self._validator(RecurringTasksRepository._RECURRING_TASKS_SCHEMA).validate(recurring_tasks_ser)
                LOGGER.info("Checked recurring tasks structure")

                yaml.dump(recurring_tasks_ser, recurring_tasks_file)
                LOGGER.info("Saved recurring tasks")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    @staticmethod
    def _find_recurring_task_by_id(ref_id: RefId, recurring_tasks: List[RecurringTask]) -> Optional[RecurringTask]:
        try:
            return next(rt for rt in recurring_tasks if rt.ref_id == ref_id)
        except StopIteration:
            return None
