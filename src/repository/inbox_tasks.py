"""Repository for inbox tasks."""

from dataclasses import dataclass
import logging
import os.path
import typing
from typing import Final, Any, ClassVar, Dict, Iterable, List, Optional, Tuple, Set

import jsonschema as js
import yaml
import pendulum

from models.basic import EntityId, Eisen, Difficulty, InboxTaskStatus
from repository.common import RepositoryError

LOGGER = logging.getLogger(__name__)


@typing.final
@dataclass()
class InboxTask:
    """An inbox task."""

    ref_id: EntityId
    project_ref_id: EntityId
    big_plan_ref_id: Optional[EntityId]
    recurring_task_ref_id: Optional[EntityId]
    created_date: pendulum.DateTime
    name: str
    archived: bool
    status: InboxTaskStatus
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    due_date: Optional[pendulum.DateTime]
    recurring_task_timeline: Optional[str]

    @property
    def is_considered_done(self) -> bool:
        """Whether the task is considered in a done-like state - either DONE or NOT_DONE."""
        return self.status == InboxTaskStatus.DONE or self.status == InboxTaskStatus.NOT_DONE


@typing.final
class InboxTasksRepository:
    """A repository of the inbox tasks."""

    _INBOX_TASKS_FILE_PATH: ClassVar[str] = "/data/inbox-tasks.yaml"

    _INBOX_TASKS_SCHEMA: ClassVar[Dict[str, Any]] = {
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
                        "big_plan_ref_id": {"type": "string"},
                        "recurring_tasks_ref_id": {"type": "string"},
                        "created_date": {"type": "string"},
                        "name": {"type": "string"},
                        "archived": {"type": "boolean"},
                        "eisen": {
                            "type": "array",
                            "entries": {"type": "string"}
                        },
                        "difficulty": {"type": "string"},
                        "due_date": {"type": "string"},
                        "recurring_task_timeline": {"type": "string"}
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
        if os.path.exists(InboxTasksRepository._INBOX_TASKS_FILE_PATH):
            return
        self._bulk_save_inbox_tasks((0, []))

    def create_inbox_task(
            self, project_ref_id: EntityId, big_plan_ref_id: Optional[EntityId],
            recurring_task_ref_id: Optional[EntityId], created_date: pendulum.DateTime, name: str, archived: bool,
            status: InboxTaskStatus, eisen: Iterable[Eisen], difficulty: Optional[Difficulty],
            due_date: Optional[pendulum.DateTime], recurring_task_timeline: Optional[str]) -> InboxTask:
        """Create a recurring task."""
        inbox_tasks_next_idx, inbox_tasks = self._bulk_load_inbox_tasks()

        new_inbox_task = InboxTask(
            ref_id=EntityId(str(inbox_tasks_next_idx)),
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            recurring_task_ref_id=recurring_task_ref_id,
            created_date=created_date,
            name=name,
            archived=archived,
            status=status,
            eisen=list(eisen),
            difficulty=difficulty,
            due_date=due_date,
            recurring_task_timeline=recurring_task_timeline)

        inbox_tasks_next_idx += 1
        inbox_tasks.append(new_inbox_task)

        self._bulk_save_inbox_tasks((inbox_tasks_next_idx, inbox_tasks))

        return new_inbox_task

    def remove_inbox_task_by_id(self, ref_id: EntityId) -> None:
        """Remove a particular inbox task."""
        inbox_tasks_next_idx, inbox_tasks = self._bulk_load_inbox_tasks()

        for inbox_task in inbox_tasks:
            if inbox_task.ref_id == ref_id:
                inbox_task.archived = True
                break
        else:
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")

        self._bulk_save_inbox_tasks((inbox_tasks_next_idx, inbox_tasks))

    def list_all_inbox_tasks(
            self,
            filter_project_ref_id: Optional[Iterable[EntityId]] = None,
            filter_big_plan_ref_id: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_id: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTask]:
        """Retrieve all the inbox tasks defined."""
        _, inbox_tasks = self._bulk_load_inbox_tasks(
            filter_project_ref_id=frozenset(filter_project_ref_id) if filter_project_ref_id else None,
            filter_big_plan_ref_id=frozenset(filter_big_plan_ref_id) if filter_big_plan_ref_id else None,
            filter_recurring_task_ref_id=frozenset(filter_recurring_task_ref_id)
            if filter_recurring_task_ref_id else None)
        return inbox_tasks

    def load_inbox_task_by_id(self, ref_id: EntityId) -> InboxTask:
        """Retrieve a particular inbox task by its id."""
        _, inbox_tasks = self._bulk_load_inbox_tasks()
        found_inbox_tasks = self._find_inbox_task_by_id(ref_id, inbox_tasks)
        if not found_inbox_tasks:
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")
        return found_inbox_tasks

    def save_inbox_task(self, new_inbox_task: InboxTask) -> None:
        """Store a particular inbox task with all new properties."""
        inbox_tasks_next_idx, inbox_tasks = self._bulk_load_inbox_tasks()

        if not self._find_inbox_task_by_id(new_inbox_task.ref_id, inbox_tasks):
            raise RepositoryError(f"Inbox task with id='{new_inbox_task.ref_id}' does not exist")

        new_inbox_tasks = [(rt if rt.ref_id != new_inbox_task.ref_id else new_inbox_task)
                           for rt in inbox_tasks]
        self._bulk_save_inbox_tasks((inbox_tasks_next_idx, new_inbox_tasks))

    def _bulk_load_inbox_tasks(
            self,
            filter_project_ref_id: Optional[Set[EntityId]] = None,
            filter_big_plan_ref_id: Optional[Set[EntityId]] = None,
            filter_recurring_task_ref_id: Optional[Set[EntityId]] = None) -> Tuple[int, List[InboxTask]]:
        try:
            with open(InboxTasksRepository._INBOX_TASKS_FILE_PATH, "r") as inbox_tasks_file:
                inbox_tasks_ser = yaml.safe_load(inbox_tasks_file)
                LOGGER.info("Loaded inbox tasks data")

                self._validator(InboxTasksRepository._INBOX_TASKS_SCHEMA).validate(inbox_tasks_ser)
                LOGGER.info("Checked inbox tasks structure")

                inbox_tasks_next_idx = inbox_tasks_ser["next_idx"]
                inbox_tasks_iter = \
                    (InboxTask(
                        ref_id=EntityId(it["ref_id"]),
                        project_ref_id=EntityId(it["project_ref_id"]),
                        big_plan_ref_id=EntityId(it["big_plan_ref_id"]) if it["big_plan_ref_id"] else None,
                        recurring_task_ref_id=
                        EntityId(it["recurring_task_ref_id"]) if it["recurring_task_ref_id"] else None,
                        created_date=pendulum.parse(it["created_date"]),
                        name=it["name"],
                        archived=it["archived"],
                        status=InboxTaskStatus(it["status"]),
                        eisen=[Eisen(e) for e in it["eisen"]],
                        difficulty=Difficulty(it["difficulty"]) if it["difficulty"] else None,
                        due_date=pendulum.parse(it["due_date"]) if it["due_date"] else None,
                        recurring_task_timeline=it.get("recurring_task_timeline", None))
                     for it in inbox_tasks_ser["entries"])
                inbox_tasks = list(rt for rt in inbox_tasks_iter
                                   if (rt.archived is False)
                                   and (filter_project_ref_id is None or rt.project_ref_id in filter_project_ref_id)
                                   and (filter_big_plan_ref_id is None or rt.big_plan_ref_id in filter_big_plan_ref_id)
                                   and (filter_recurring_task_ref_id is None
                                        or rt.recurring_task_ref_id in filter_recurring_task_ref_id))

                return inbox_tasks_next_idx, inbox_tasks
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    def _bulk_save_inbox_tasks(self, bulk_data: Tuple[int, List[InboxTask]]) -> None:
        try:
            with open(InboxTasksRepository._INBOX_TASKS_FILE_PATH, "w") as inbox_tasks_file:
                inbox_tasks_ser = {
                    "next_idx": bulk_data[0],
                    "entries": [{
                        "ref_id": it.ref_id,
                        "project_ref_id": it.project_ref_id,
                        "big_plan_ref_id": it.big_plan_ref_id,
                        "recurring_task_ref_id": it.recurring_task_ref_id,
                        "created_date": it.created_date.to_datetime_string(),
                        "name": it.name,
                        "archived": it.archived,
                        "status": it.status.value,
                        "eisen": [e.value for e in it.eisen],
                        "difficulty": it.difficulty.value if it.difficulty else None,
                        "due_date": it.due_date.to_datetime_string() if it.due_date else None,
                        "recurring_task_timeline": it.recurring_task_timeline
                    } for it in bulk_data[1]]
                }

                self._validator(InboxTasksRepository._INBOX_TASKS_SCHEMA).validate(inbox_tasks_ser)
                LOGGER.info("Checked inbox tasks structure")

                yaml.dump(inbox_tasks_ser, inbox_tasks_file)
                LOGGER.info("Saved inbox tasks")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    @staticmethod
    def _find_inbox_task_by_id(ref_id: EntityId, inbox_tasks: List[InboxTask]) -> Optional[InboxTask]:
        try:
            return next(it for it in inbox_tasks if it.ref_id == ref_id)
        except StopIteration:
            return None
