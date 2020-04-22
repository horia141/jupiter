"""Repository for inbox tasks."""

import logging
import enum
import os.path
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Tuple, Set

import jsonschema as js
import yaml
import pendulum

from repository.common import RefId, RepositoryError, TaskEisen, TaskDifficulty

LOGGER = logging.getLogger(__name__)


@enum.unique
class InboxTaskStatus(enum.Enum):
    """The status of an inbox task."""
    NOT_STARTED = "not-started"
    ACCEPTED = "accepted"
    RECURRING = "recurring"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    NOT_DONE = "not-done"
    DONE = "done"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))


class InboxTask:
    """An inbox task."""

    _ref_id: RefId
    _project_ref_id: RefId
    _big_plan_ref_id: Optional[RefId]
    _recurring_task_ref_id: Optional[RefId]
    _created_date: pendulum.DateTime
    _name: str
    _archived: bool
    _status: InboxTaskStatus
    _eisen: List[TaskEisen]
    _difficulty: Optional[TaskDifficulty]
    _due_date: Optional[pendulum.DateTime]
    _recurring_task_timeline: Optional[str]

    def __init__(
            self, ref_id: RefId, project_ref_id: RefId, big_plan_ref_id: Optional[RefId],
            recurring_task_ref_id: Optional[RefId], created_date: pendulum.DateTime, name: str,
            archived: bool, status: InboxTaskStatus, eisen: List[TaskEisen], difficulty: Optional[TaskDifficulty],
            due_date: Optional[pendulum.DateTime], recurring_task_timeline: Optional[str]) -> None:
        """Constructor."""
        self._ref_id = ref_id
        self._project_ref_id = project_ref_id
        self._big_plan_ref_id = big_plan_ref_id
        self._recurring_task_ref_id = recurring_task_ref_id
        self._created_date = created_date
        self._name = name
        self._archived = archived
        self._status = status
        self._eisen = eisen
        self._difficulty = difficulty
        self._due_date = due_date
        self._recurring_task_timeline = recurring_task_timeline

    def is_considered_done(self) -> bool:
        """Whether the task is considered done or not."""
        return self._status == InboxTaskStatus.DONE or self._status == InboxTaskStatus.NOT_DONE

    def set_big_plan_ref_id(self, big_plan_ref_id: Optional[RefId]) -> None:
        """Change the big plan this inbox task is attached to."""
        self._big_plan_ref_id = big_plan_ref_id

    def set_name(self, name: str) -> None:
        """Change the name of the recurring task."""
        self._name = name

    def set_archived(self, archived: bool) -> None:
        """Change the archived status of a task."""
        self._archived = archived

    def set_status(self, status: InboxTaskStatus) -> None:
        """Change the status of a task."""
        self._status = status

    def set_eisen(self, eisen: Iterable[TaskEisen]) -> None:
        """Change the Eisenhower status of a task."""
        self._eisen = list(eisen)

    def set_difficulty(self, difficulty: Optional[TaskDifficulty]) -> None:
        """Change the difficulty of the task."""
        self._difficulty = difficulty

    def set_due_date(self, due_date: Optional[pendulum.DateTime]) -> None:
        """Change the due date of the task."""
        self._due_date = due_date

    def set_recurring_task_timeline(self, recurring_task_timeline: Optional[str]) -> None:
        """Change the timeline of the recurring task."""
        self._recurring_task_timeline = recurring_task_timeline

    @property
    def ref_id(self) -> RefId:
        """The id of the inbox task."""
        return self._ref_id

    @property
    def project_ref_id(self) -> RefId:
        """The id of the project to which the inbox task belongs."""
        return self._project_ref_id

    @property
    def big_plan_ref_id(self) -> Optional[RefId]:
        """The id of a big plan to which the inbox task may be attached."""
        return self._big_plan_ref_id

    @property
    def recurring_task_ref_id(self) -> Optional[RefId]:
        """The id of a recurring task to which the inbox task may be attached."""
        return self._recurring_task_ref_id

    @property
    def created_date(self) -> pendulum.DateTime:
        """The time the inbox task was created."""
        return self._created_date

    @property
    def name(self) -> str:
        """The name of the inbox task."""
        return self._name

    @property
    def archived(self) -> bool:
        """The archived status of inbox task."""
        return self._archived

    @property
    def status(self) -> InboxTaskStatus:
        """The status of the inbox task."""
        return self._status

    @property
    def eisen(self) -> Iterable[TaskEisen]:
        """The Eisenhower status of the inbox task."""
        return self._eisen

    @property
    def difficulty(self) -> Optional[TaskDifficulty]:
        """The difficulty of the inbox task."""
        return self._difficulty

    @property
    def due_date(self) -> Optional[pendulum.DateTime]:
        """The due date of the inbox task."""
        return self._due_date

    @property
    def recurring_task_timeline(self) -> Optional[str]:
        """The timeline for this task if it's a recurring one."""
        return self._recurring_task_timeline


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

    _validator: Any

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
            self, project_ref_id: RefId, big_plan_ref_id: Optional[RefId], recurring_task_ref_id: Optional[RefId],
            created_date: pendulum.DateTime, name: str, archived: bool, status: InboxTaskStatus,
            eisen: Iterable[TaskEisen], difficulty: Optional[TaskDifficulty],
            due_date: Optional[pendulum.DateTime], recurring_task_timeline: Optional[str]) -> InboxTask:
        """Create a recurring task."""
        inbox_tasks_next_idx, inbox_tasks = self._bulk_load_inbox_tasks()

        new_inbox_task = InboxTask(
            ref_id=RefId(str(inbox_tasks_next_idx)),
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

    def remove_inbox_task_by_id(self, ref_id: RefId) -> None:
        """Remove a particular inbox task."""
        inbox_tasks_next_idx, inbox_tasks = self._bulk_load_inbox_tasks()

        if not self._find_inbox_task_by_id(ref_id, inbox_tasks):
            raise RepositoryError(f"Inbox task with id='{ref_id}' does not exist")

        new_inbox_tasks = filter(lambda p: p.ref_id != ref_id, inbox_tasks)
        self._bulk_save_inbox_tasks((inbox_tasks_next_idx, new_inbox_tasks))

    def list_all_inbox_tasks(
            self,
            filter_project_ref_id: Optional[Iterable[RefId]] = None,
            filter_big_plan_ref_id: Optional[Iterable[RefId]] = None,
            filter_recurring_task_ref_id: Optional[Iterable[RefId]] = None) -> Iterable[InboxTask]:
        """Retrieve all the inbox tasks defined."""
        _, inbox_tasks = self._bulk_load_inbox_tasks(
            filter_project_ref_id=frozenset(filter_project_ref_id) if filter_project_ref_id else None,
            filter_big_plan_ref_id=frozenset(filter_big_plan_ref_id) if filter_big_plan_ref_id else None,
            filter_recurring_task_ref_id=frozenset(filter_recurring_task_ref_id)
            if filter_recurring_task_ref_id else None)
        return inbox_tasks

    def load_inbox_task_by_id(self, ref_id: RefId) -> InboxTask:
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
            filter_project_ref_id: Optional[Set[RefId]] = None,
            filter_big_plan_ref_id: Optional[Set[RefId]] = None,
            filter_recurring_task_ref_id: Optional[Set[RefId]] = None) -> Tuple[int, List[InboxTask]]:
        try:
            with open(InboxTasksRepository._INBOX_TASKS_FILE_PATH, "r") as inbox_tasks_file:
                inbox_tasks_ser = yaml.safe_load(inbox_tasks_file)
                LOGGER.info("Loaded inbox tasks data")

                self._validator(InboxTasksRepository._INBOX_TASKS_SCHEMA).validate(inbox_tasks_ser)
                LOGGER.info("Checked inbox tasks structure")

                inbox_tasks_next_idx = inbox_tasks_ser["next_idx"]
                inbox_tasks_iter = \
                    (InboxTask(
                        ref_id=RefId(it["ref_id"]),
                        project_ref_id=RefId(it["project_ref_id"]),
                        big_plan_ref_id=RefId(it["big_plan_ref_id"]) if it["big_plan_ref_id"] else None,
                        recurring_task_ref_id=
                        RefId(it["recurring_task_ref_id"]) if it["recurring_task_ref_id"] else None,
                        created_date=pendulum.parse(it["created_date"]),
                        name=it["name"],
                        archived=it["archived"],
                        status=InboxTaskStatus(it["status"]),
                        eisen=[TaskEisen(e) for e in it["eisen"]],
                        difficulty=TaskDifficulty(it["difficulty"]) if it["difficulty"] else None,
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

    def _bulk_save_inbox_tasks(self, bulk_data: Tuple[int, Iterable[InboxTask]]) -> None:
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
    def _find_inbox_task_by_id(ref_id: RefId, inbox_tasks: Iterable[InboxTask]) -> Optional[InboxTask]:
        try:
            return next(it for it in inbox_tasks if it.ref_id == ref_id)
        except StopIteration:
            return None
