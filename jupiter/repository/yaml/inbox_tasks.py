"""Repository for inbox tasks."""
import logging
import typing
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_collection_repository import InboxTaskCollectionRepository, \
    InboxTaskCollectionAlreadyExistsError, InboxTaskCollectionNotFoundError
from jupiter.domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository, InboxTaskNotFoundError
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.repository.yaml.infra.storage import BaseEntityRow, EntitiesStorage, In, Eq, StorageEntityNotFoundError
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _InboxTaskCollectionRow(BaseEntityRow):
    """A container for inbox tasks."""
    project_ref_id: EntityId


class YamlInboxTaskCollectionRepository(InboxTaskCollectionRepository):
    """A repository for inbox task collections."""

    _INBOX_TASK_COLLECTIONS_FILE_PATH: ClassVar[Path] = Path("./inbox-task-collections")
    _INBOX_TASK_COLLECTIONS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_InboxTaskCollectionRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_InboxTaskCollectionRow](
            self._INBOX_TASK_COLLECTIONS_FILE_PATH, self._INBOX_TASK_COLLECTIONS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlInboxTaskCollectionRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, inbox_task_collection: InboxTaskCollection) -> InboxTaskCollection:
        """Create a inbox task collection."""
        inbox_task_collection_rows = \
            self._storage.find_all(allow_archived=True, project_ref_id=Eq(inbox_task_collection.project_ref_id))

        if len(inbox_task_collection_rows) > 0:
            raise InboxTaskCollectionAlreadyExistsError(
                f"Inbox task collection for project ='{inbox_task_collection.project_ref_id}' already exists")

        new_inbox_task_collection_row = self._storage.create(_InboxTaskCollectionRow(
            archived=inbox_task_collection.archived,
            project_ref_id=inbox_task_collection.project_ref_id))
        inbox_task_collection.assign_ref_id(new_inbox_task_collection_row.ref_id)
        return inbox_task_collection

    def save(self, inbox_task_collection: InboxTaskCollection) -> InboxTaskCollection:
        """Save an inbox task collection collection."""
        try:
            return self._row_to_entity(self._storage.update(self._entity_to_row(inbox_task_collection)))
        except StorageEntityNotFoundError as err:
            raise InboxTaskCollectionNotFoundError(
                f"Inbox task task collection with id {inbox_task_collection.ref_id} does not exist") from err

    def load_by_id(self, ref_id: EntityId) -> InboxTaskCollection:
        """Load an inbox task collection by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=False))
        except StorageEntityNotFoundError as err:
            raise InboxTaskCollectionNotFoundError(f"Inbox task collection with id {ref_id} does not exist") from err

    def load_by_project(self, project_ref_id: EntityId) -> InboxTaskCollection:
        """Find an inbox task collection by project ref id."""
        try:
            inbox_task_collection_row = \
                self._storage.find_first(allow_archived=False, project_ref_id=Eq(project_ref_id))
            return self._row_to_entity(inbox_task_collection_row)
        except StorageEntityNotFoundError as err:
            raise InboxTaskCollectionNotFoundError(
                f"Inbox task collection for project id {project_ref_id} does not exist") from err

    def find_all(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTaskCollection]:
        """Retrieve inbox task collections."""
        return [self._row_to_entity(itr) for itr in self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(*filter_project_ref_ids) if filter_project_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> InboxTaskCollection:
        """Hard remove an inbox task collection - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id=ref_id))
        except StorageEntityNotFoundError as err:
            raise InboxTaskCollectionNotFoundError(f"Inbox task collection with id {ref_id} does not exist") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _InboxTaskCollectionRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _InboxTaskCollectionRow(
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _InboxTaskCollectionRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": str(live_form.project_ref_id)
        }

    @staticmethod
    def _entity_to_row(inbox_task_collection: InboxTaskCollection) -> _InboxTaskCollectionRow:
        inbox_task_collection_row = _InboxTaskCollectionRow(
            archived=inbox_task_collection.archived,
            project_ref_id=inbox_task_collection.project_ref_id)
        inbox_task_collection_row.ref_id = inbox_task_collection.ref_id
        inbox_task_collection_row.created_time = inbox_task_collection.created_time
        inbox_task_collection_row.archived_time = inbox_task_collection.archived_time
        inbox_task_collection_row.last_modified_time = inbox_task_collection.last_modified_time
        return inbox_task_collection_row

    @staticmethod
    def _row_to_entity(row: _InboxTaskCollectionRow) -> InboxTaskCollection:
        return InboxTaskCollection(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            project_ref_id=row.project_ref_id)


@dataclass()
class _InboxTaskRow(BaseEntityRow):
    """An inbox task."""

    inbox_task_collection_ref_id: EntityId
    source: InboxTaskSource
    big_plan_ref_id: Optional[EntityId]
    recurring_task_ref_id: Optional[EntityId]
    metric_ref_id: Optional[EntityId]
    person_ref_id: Optional[EntityId]
    name: InboxTaskName
    archived: bool
    status: InboxTaskStatus
    eisen: Eisen
    difficulty: Optional[Difficulty]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    recurring_timeline: Optional[str]
    recurring_type: Optional[RecurringTaskType]
    recurring_gen_right_now: Optional[Timestamp]  # Time for which this inbox task was generated
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


class YamlInboxTaskRepository(InboxTaskRepository):
    """A repository of the inbox tasks."""

    _INBOX_TASKS_FILE_PATH: ClassVar[Path] = Path("./inbox-tasks")
    _INBOX_TASKS_NUM_SHARDS: ClassVar[int] = 50

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[_InboxTaskRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[_InboxTaskRow](
            self._INBOX_TASKS_FILE_PATH, self._INBOX_TASKS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlInboxTaskRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, inbox_task_collection: InboxTaskCollection, inbox_task: InboxTask) -> InboxTask:
        """Create a inbox task."""
        new_inbox_task_row = self._storage.create(_InboxTaskRow(
            inbox_task_collection_ref_id=inbox_task_collection.ref_id,
            source=inbox_task.source,
            big_plan_ref_id=inbox_task.big_plan_ref_id,
            recurring_task_ref_id=inbox_task.recurring_task_ref_id,
            metric_ref_id=inbox_task.metric_ref_id,
            person_ref_id=inbox_task.person_ref_id,
            name=inbox_task.name,
            archived=inbox_task.archived,
            status=inbox_task.status,
            eisen=inbox_task.eisen,
            difficulty=inbox_task.difficulty,
            actionable_date=inbox_task.actionable_date,
            due_date=inbox_task.due_date,
            recurring_timeline=inbox_task.recurring_timeline,
            recurring_type=inbox_task.recurring_type,
            recurring_gen_right_now=inbox_task.recurring_gen_right_now,
            accepted_time=inbox_task.accepted_time,
            working_time=inbox_task.working_time,
            completed_time=inbox_task.completed_time))
        inbox_task.assign_ref_id(new_inbox_task_row.ref_id)
        return inbox_task

    def save(self, inbox_task: InboxTask) -> InboxTask:
        """Save a inbox task - it should already exist."""
        try:
            inbox_task_row = self._entity_to_row(inbox_task)
            inbox_task_row = self._storage.update(inbox_task_row)
            return self._row_to_entity(inbox_task_row)
        except StorageEntityNotFoundError as err:
            raise InboxTaskNotFoundError(f"Inbox task with id {inbox_task.ref_id} does not exist") from err

    def dump_all(self, inbox_tasks: Iterable[InboxTask]) -> None:
        """Save all inbox tasks - good for migrations."""
        self._storage.dump_all(self._entity_to_row(it) for it in inbox_tasks)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTask:
        """Load a inbox task by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))
        except StorageEntityNotFoundError as err:
            raise InboxTaskNotFoundError(f"Inbox task with id {ref_id} does not exist") from err

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_inbox_task_collection_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_sources: Optional[Iterable[InboxTaskSource]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_person_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTask]:
        """Find all inbox tasks."""
        return [self._row_to_entity(itr) for itr in self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            inbox_task_collection_ref_id=In(*filter_inbox_task_collection_ref_ids)
            if filter_inbox_task_collection_ref_ids else None,
            source=In(*filter_sources) if filter_sources else None,
            big_plan_ref_id=In(*filter_big_plan_ref_ids) if filter_big_plan_ref_ids else None,
            recurring_task_ref_id=In(*filter_recurring_task_ref_ids) if filter_recurring_task_ref_ids else None,
            metric_ref_id=In(*filter_metric_ref_ids) if filter_metric_ref_ids else None,
            person_ref_id=In(*filter_person_ref_ids) if filter_person_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> InboxTask:
        """Hard remove a inbox task - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id))
        except StorageEntityNotFoundError as err:
            raise InboxTaskNotFoundError(f"Inbox task with id {ref_id} does not exist") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "inbox_task_collection_ref_id": {"type": "string"},
            "source": {"type": ["string", "null"]},
            "big_plan_ref_id": {"type": ["string", "null"]},
            "recurring_tasks_ref_id": {"type": ["string", "null"]},
            "metric_ref_id": {"type": ["string", "null"]},
            "person_ref_id": {"type": ["string", "null"]},
            "name": {"type": "string"},
            "archived": {"type": "boolean"},
            "eisen": {"type": ["string"]},
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
    def storage_to_live(storage_form: JSONDictType) -> _InboxTaskRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _InboxTaskRow(
            inbox_task_collection_ref_id=EntityId(typing.cast(str, storage_form["inbox_task_collection_ref_id"])),
            source=InboxTaskSource.from_raw(typing.cast(str, storage_form["source"])),
            big_plan_ref_id=EntityId(typing.cast(str, storage_form["big_plan_ref_id"]))
            if storage_form["big_plan_ref_id"] else None,
            recurring_task_ref_id=EntityId(typing.cast(str, (storage_form["recurring_task_ref_id"])))
            if storage_form["recurring_task_ref_id"] else None,
            metric_ref_id=EntityId(typing.cast(str, storage_form["metric_ref_id"]))
            if storage_form["metric_ref_id"] else None,
            person_ref_id=EntityId(typing.cast(str, storage_form["person_ref_id"]))
            if storage_form.get("person_ref_id", None) else None,
            name=InboxTaskName.from_raw(typing.cast(str, storage_form["name"])),
            archived=typing.cast(bool, storage_form["archived"]),
            status=InboxTaskStatus(typing.cast(str, storage_form["status"])),
            eisen=Eisen.from_raw(typing.cast(str, storage_form["eisen"])),
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
    def live_to_storage(live_form: _InboxTaskRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "inbox_task_collection_ref_id": str(live_form.inbox_task_collection_ref_id),
            "source": live_form.source.value,
            "big_plan_ref_id": str(live_form.big_plan_ref_id) if live_form.big_plan_ref_id else None,
            "recurring_task_ref_id": str(live_form.recurring_task_ref_id) if live_form.recurring_task_ref_id else None,
            "metric_ref_id": str(live_form.metric_ref_id) if live_form.metric_ref_id else None,
            "person_ref_id": str(live_form.person_ref_id) if live_form.person_ref_id else None,
            "name": str(live_form.name),
            "status": live_form.status.value,
            "eisen": live_form.eisen.value,
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

    @staticmethod
    def _entity_to_row(inbox_task: InboxTask) -> _InboxTaskRow:
        inbox_task_row = _InboxTaskRow(
            inbox_task_collection_ref_id=inbox_task.inbox_task_collection_ref_id,
            source=inbox_task.source,
            big_plan_ref_id=inbox_task.big_plan_ref_id,
            recurring_task_ref_id=inbox_task.recurring_task_ref_id,
            metric_ref_id=inbox_task.metric_ref_id,
            person_ref_id=inbox_task.person_ref_id,
            name=inbox_task.name,
            archived=inbox_task.archived,
            status=inbox_task.status,
            eisen=inbox_task.eisen,
            difficulty=inbox_task.difficulty,
            actionable_date=inbox_task.actionable_date,
            due_date=inbox_task.due_date,
            recurring_timeline=inbox_task.recurring_timeline,
            recurring_type=inbox_task.recurring_type,
            recurring_gen_right_now=inbox_task.recurring_gen_right_now,
            accepted_time=inbox_task.accepted_time,
            working_time=inbox_task.working_time,
            completed_time=inbox_task.completed_time)
        inbox_task_row.ref_id = inbox_task.ref_id
        inbox_task_row.created_time = inbox_task.created_time
        inbox_task_row.archived_time = inbox_task.archived_time
        inbox_task_row.last_modified_time = inbox_task.last_modified_time
        return inbox_task_row

    @staticmethod
    def _row_to_entity(row: _InboxTaskRow) -> InboxTask:
        return InboxTask(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            inbox_task_collection_ref_id=row.inbox_task_collection_ref_id,
            source=row.source,
            big_plan_ref_id=row.big_plan_ref_id,
            recurring_task_ref_id=row.recurring_task_ref_id,
            metric_ref_id=row.metric_ref_id,
            person_ref_id=row.person_ref_id,
            name=row.name,
            status=row.status,
            eisen=row.eisen,
            difficulty=row.difficulty,
            actionable_date=row.actionable_date,
            due_date=row.due_date,
            recurring_timeline=row.recurring_timeline,
            recurring_type=row.recurring_type,
            recurring_gen_right_now=row.recurring_gen_right_now,
            accepted_time=row.accepted_time,
            working_time=row.working_time,
            completed_time=row.completed_time)
