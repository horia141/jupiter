"""Repository for recurring tasks."""
import logging
import typing
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, Optional

import pendulum

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.infra.recurring_task_collection_repository \
    import RecurringTaskCollectionRepository, RecurringTaskCollectionAlreadyExistsError, \
    RecurringTaskCollectionNotFoundError
from jupiter.domain.recurring_tasks.infra.recurring_task_repository import RecurringTaskRepository, \
    RecurringTaskNotFoundError
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from jupiter.domain.recurring_tasks.recurring_task_name import RecurringTaskName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.json import JSONDictType
from jupiter.repository.yaml.infra.storage import BaseEntityRow, EntitiesStorage, In, Eq, StorageEntityNotFoundError
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _RecurringTaskCollectionRow(BaseEntityRow):
    """A container for recurring tasks."""
    project_ref_id: EntityId


class YamlRecurringTaskCollectionRepository(RecurringTaskCollectionRepository):
    """A repository for recurring task collections."""

    _INBOX_TASK_COLLECTIONS_FILE_PATH: ClassVar[Path] = Path("./recurring-task-collections")
    _INBOX_TASK_COLLECTIONS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_RecurringTaskCollectionRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_RecurringTaskCollectionRow](
            self._INBOX_TASK_COLLECTIONS_FILE_PATH, self._INBOX_TASK_COLLECTIONS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlRecurringTaskCollectionRepository':
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

    def create(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Create a recurring task collection."""
        recurring_task_collection_rows = \
            self._storage.find_all(allow_archived=True, project_ref_id=Eq(recurring_task_collection.project_ref_id))

        if len(recurring_task_collection_rows) > 0:
            raise RecurringTaskCollectionAlreadyExistsError(
                f"Recurring task collection for project ='{recurring_task_collection.project_ref_id}' already exists")

        new_recurring_task_collection_row = self._storage.create(_RecurringTaskCollectionRow(
            archived=recurring_task_collection.archived,
            project_ref_id=recurring_task_collection.project_ref_id))
        recurring_task_collection = recurring_task_collection.assign_ref_id(new_recurring_task_collection_row.ref_id)
        return recurring_task_collection

    def save(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Save an inbox task collection collection."""
        try:
            return self._row_to_entity(self._storage.update(self._entity_to_row(recurring_task_collection)))
        except StorageEntityNotFoundError as err:
            raise RecurringTaskCollectionNotFoundError(
                f"Recurring task task collection with id {recurring_task_collection.ref_id} does not exist") from err

    def dump_all(self, recurring_task_collection: Iterable[RecurringTaskCollection]) -> None:
        """Save all inbox tasks - good for migrations."""
        self._storage.dump_all(self._entity_to_row(it) for it in recurring_task_collection)

    def load_by_id(self, ref_id: EntityId) -> RecurringTaskCollection:
        """Load an inbox task collection by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=False))
        except StorageEntityNotFoundError as err:
            raise RecurringTaskCollectionNotFoundError(
                f"Recurring task collection with id {ref_id} does not exist") from err

    def load_by_project(self, project_ref_id: EntityId) -> RecurringTaskCollection:
        """Find an recurring task collection by project ref id."""
        try:
            recurring_task_collection_row = \
                self._storage.find_first(allow_archived=False, project_ref_id=Eq(project_ref_id))
            return self._row_to_entity(recurring_task_collection_row)
        except StorageEntityNotFoundError as err:
            raise RecurringTaskCollectionNotFoundError(
                f"Recurring task collection for project with id {project_ref_id} does not exist") from err

    def find_all(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTaskCollection]:
        """Retrieve inbox task collections."""
        return [self._row_to_entity(itr) for itr in self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(
                *filter_project_ref_ids) if filter_project_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> RecurringTaskCollection:
        """Hard remove an recurring task collection - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id=ref_id))
        except StorageEntityNotFoundError as err:
            raise RecurringTaskCollectionNotFoundError(
                f"Recurring task collection with id {ref_id} does not exist") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _RecurringTaskCollectionRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _RecurringTaskCollectionRow(
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _RecurringTaskCollectionRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": str(live_form.project_ref_id)
        }

    @staticmethod
    def _entity_to_row(recurring_task_collection: RecurringTaskCollection) -> _RecurringTaskCollectionRow:
        recurring_task_collection_row = _RecurringTaskCollectionRow(
            archived=recurring_task_collection.archived,
            project_ref_id=recurring_task_collection.project_ref_id)
        recurring_task_collection_row.ref_id = recurring_task_collection.ref_id
        recurring_task_collection_row.version = recurring_task_collection.version
        recurring_task_collection_row.created_time = recurring_task_collection.created_time
        recurring_task_collection_row.archived_time = recurring_task_collection.archived_time
        recurring_task_collection_row.last_modified_time = recurring_task_collection.last_modified_time
        return recurring_task_collection_row

    @staticmethod
    def _row_to_entity(row: _RecurringTaskCollectionRow) -> RecurringTaskCollection:
        return RecurringTaskCollection(
            ref_id=row.ref_id,
            version=row.version,
            archived=row.archived,
            created_time=row.created_time,
            archived_time=row.archived_time,
            last_modified_time=row.last_modified_time,
            events=[],
            project_ref_id=row.project_ref_id)


@dataclass()
class _RecurringTaskRow(BaseEntityRow):
    """A recurring task."""

    recurring_task_collection_ref_id: EntityId
    name: RecurringTaskName
    period: RecurringTaskPeriod
    the_type: RecurringTaskType
    eisen: Eisen
    difficulty: Optional[Difficulty]
    actionable_from_day: Optional[RecurringTaskDueAtDay]
    actionable_from_month: Optional[RecurringTaskDueAtMonth]
    due_at_time: Optional[RecurringTaskDueAtTime]
    due_at_day: Optional[RecurringTaskDueAtDay]
    due_at_month: Optional[RecurringTaskDueAtMonth]
    suspended: bool
    skip_rule: Optional[RecurringTaskSkipRule]
    must_do: bool
    start_at_date: ADate
    end_at_date: Optional[ADate]


@typing.final
class YamlRecurringTaskRepository(RecurringTaskRepository):
    """A repository for recurring tasks."""

    _RECURRING_TASKS_FILE_PATH: ClassVar[Path] = Path("./recurring-tasks")
    _RECURRING_TASKS_NUM_SHARDS: ClassVar[int] = 10

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[_RecurringTaskRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[_RecurringTaskRow](
            self._RECURRING_TASKS_FILE_PATH, self._RECURRING_TASKS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlRecurringTaskRepository':
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

    def create(
            self, recurring_task_collection: RecurringTaskCollection, recurring_task: RecurringTask) -> RecurringTask:
        """Create a recurring task."""
        new_recurring_task_row = self._storage.create(_RecurringTaskRow(
            recurring_task_collection_ref_id=recurring_task_collection.ref_id,
            archived=recurring_task.archived,
            name=recurring_task.name,
            period=recurring_task.period,
            the_type=recurring_task.the_type,
            eisen=recurring_task.gen_params.eisen,
            difficulty=recurring_task.gen_params.difficulty,
            actionable_from_day=recurring_task.gen_params.actionable_from_day,
            actionable_from_month=recurring_task.gen_params.actionable_from_month,
            due_at_time=recurring_task.gen_params.due_at_time,
            due_at_day=recurring_task.gen_params.due_at_day,
            due_at_month=recurring_task.gen_params.due_at_month,
            suspended=recurring_task.suspended,
            skip_rule=recurring_task.skip_rule,
            must_do=recurring_task.must_do,
            start_at_date=recurring_task.start_at_date,
            end_at_date=recurring_task.end_at_date))
        recurring_task = recurring_task.assign_ref_id(new_recurring_task_row.ref_id)
        return recurring_task

    def save(self, recurring_task: RecurringTask) -> RecurringTask:
        """Save a recurring task - it should already exist."""
        try:
            recurring_task_row = self._entity_to_row(recurring_task)
            recurring_task_row = self._storage.update(recurring_task_row)
            return self._row_to_entity(recurring_task_row)
        except StorageEntityNotFoundError as err:
            raise RecurringTaskNotFoundError(
                f"Recurring task with id {recurring_task.ref_id} does not exist") from err

    def dump_all(self, inbox_tasks: Iterable[RecurringTask]) -> None:
        """Save all inbox tasks - good for migrations."""
        self._storage.dump_all(self._entity_to_row(it) for it in inbox_tasks)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTask:
        """Load a recurring task by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))
        except StorageEntityNotFoundError as err:
            raise RecurringTaskNotFoundError(
                f"Recurring task with id {ref_id} does not exist") from err

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_collection_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTask]:
        """Find all recurring tasks."""
        return [self._row_to_entity(bpr) for bpr in self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            recurring_task_collection_ref_id=
            In(*filter_recurring_task_collection_ref_ids) if filter_recurring_task_collection_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> RecurringTask:
        """Hard remove a recurring task - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id))
        except StorageEntityNotFoundError as err:
            raise RecurringTaskNotFoundError(
                f"Recurring task with id {ref_id} does not exist") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "recurring_task_collection_ref_id": {"type": "string"},
            "name": {"type": "string"},
            "period": {"type": "string"},
            "the_type": {"type": "string"},
            "eisen_old": {
                "type": "array",
                "entries": {"type": "string"}
            },
            "eisen": {"type": ["string"]},
            "difficulty": {"type": ["string", "null"]},
            "actionable_from_day": {"type": ["number", "null"]},
            "actionable_from_month": {"type": ["number", "null"]},
            "due_at_time": {"type": ["string", "null"]},
            "due_at_day": {"type": ["number", "null"]},
            "due_at_month": {"type": ["number", "null"]},
            "suspended": {"type": "boolean"},
            "skip_rule": {"type": ["string", "null"]},
            "must_do": {"type": "boolean"},
            "start_at_date": {"type": ["string", "null"]},
            "end_at_date": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _RecurringTaskRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        today_hack = pendulum.today().date()
        return _RecurringTaskRow(
            recurring_task_collection_ref_id=
            EntityId(typing.cast(str, storage_form["recurring_task_collection_ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=RecurringTaskName.from_raw(typing.cast(str, storage_form["name"])),
            period=RecurringTaskPeriod(typing.cast(str, storage_form["period"])),
            the_type=RecurringTaskType(typing.cast(str, storage_form["the_type"])),
            eisen=Eisen.from_raw(typing.cast(str, storage_form["eisen"])),
            difficulty=Difficulty(typing.cast(str, storage_form["difficulty"])) if storage_form["difficulty"] else None,
            actionable_from_day=RecurringTaskDueAtDay(typing.cast(int, storage_form["actionable_from_day"]))
            if storage_form.get("actionable_from_day", None) else None,
            actionable_from_month=RecurringTaskDueAtMonth(typing.cast(int, storage_form["actionable_from_month"]))
            if storage_form.get("actionable_from_month", None) else None,
            due_at_time=RecurringTaskDueAtTime(typing.cast(str, storage_form["due_at_time"]))
            if storage_form["due_at_time"] else None,
            due_at_day=RecurringTaskDueAtDay(typing.cast(int, storage_form["due_at_day"]))
            if storage_form["due_at_day"] else None,
            due_at_month=RecurringTaskDueAtMonth(typing.cast(int, storage_form["due_at_month"]))
            if storage_form["due_at_month"] else None,
            suspended=typing.cast(bool, storage_form["suspended"]),
            skip_rule=RecurringTaskSkipRule.from_raw(typing.cast(str, storage_form["skip_rule"]))
            if storage_form["skip_rule"] else None,
            must_do=typing.cast(bool, storage_form["must_do"]),
            start_at_date=ADate.from_str(typing.cast(str, storage_form["start_at_date"]))
            if storage_form["start_at_date"] else ADate.from_date(today_hack),
            end_at_date=ADate.from_str(typing.cast(str, storage_form["end_at_date"]))
            if storage_form["end_at_date"] else None)

    @staticmethod
    def live_to_storage(live_form: _RecurringTaskRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "recurring_task_collection_ref_id": str(live_form.recurring_task_collection_ref_id),
            "name": str(live_form.name),
            "period": live_form.period.value,
            "the_type": live_form.the_type.value,
            "eisen": live_form.eisen.value,
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "actionable_from_day": live_form.actionable_from_day.as_int() if live_form.actionable_from_day else None,
            "actionable_from_month":
                live_form.actionable_from_month.as_int() if live_form.actionable_from_month else None,
            "due_at_time": str(live_form.due_at_time) if live_form.due_at_time else None,
            "due_at_day": live_form.due_at_day.as_int() if live_form.due_at_day else None,
            "due_at_month": live_form.due_at_month.as_int() if live_form.due_at_month else None,
            "suspended": live_form.suspended,
            "skip_rule": str(live_form.skip_rule),
            "must_do": live_form.must_do,
            "start_at_date": str(live_form.start_at_date),
            "end_at_date": str(live_form.end_at_date) if live_form.end_at_date else None
        }

    @staticmethod
    def _entity_to_row(recurring_task: RecurringTask) -> _RecurringTaskRow:
        recurring_task_row = _RecurringTaskRow(
            recurring_task_collection_ref_id=recurring_task.recurring_task_collection_ref_id,
            archived=recurring_task.archived,
            name=recurring_task.name,
            period=recurring_task.period,
            the_type=recurring_task.the_type,
            eisen=recurring_task.gen_params.eisen,
            difficulty=recurring_task.gen_params.difficulty,
            actionable_from_day=recurring_task.gen_params.actionable_from_day,
            actionable_from_month=recurring_task.gen_params.actionable_from_month,
            due_at_time=recurring_task.gen_params.due_at_time,
            due_at_day=recurring_task.gen_params.due_at_day,
            due_at_month=recurring_task.gen_params.due_at_month,
            suspended=recurring_task.suspended,
            skip_rule=recurring_task.skip_rule,
            must_do=recurring_task.must_do,
            start_at_date=recurring_task.start_at_date,
            end_at_date=recurring_task.end_at_date)
        recurring_task_row.ref_id = recurring_task.ref_id
        recurring_task_row.version = recurring_task.version
        recurring_task_row.created_time = recurring_task.created_time
        recurring_task_row.archived_time = recurring_task.archived_time
        recurring_task_row.last_modified_time = recurring_task.last_modified_time
        return recurring_task_row

    @staticmethod
    def _row_to_entity(row: _RecurringTaskRow) -> RecurringTask:
        return RecurringTask(
            ref_id=row.ref_id,
            version=row.version,
            archived=row.archived,
            created_time=row.created_time,
            archived_time=row.archived_time,
            last_modified_time=row.last_modified_time,
            events=[],
            recurring_task_collection_ref_id=row.recurring_task_collection_ref_id,
            name=row.name,
            period=row.period,
            the_type=row.the_type,
            gen_params=RecurringTaskGenParams(
                project_ref_id=BAD_REF_ID,
                period=row.period,
                eisen=row.eisen,
                difficulty=row.difficulty,
                actionable_from_day=row.actionable_from_day,
                actionable_from_month=row.actionable_from_month,
                due_at_time=row.due_at_time,
                due_at_day=row.due_at_day,
                due_at_month=row.due_at_month),
            suspended=row.suspended,
            skip_rule=row.skip_rule,
            must_do=row.must_do,
            start_at_date=row.start_at_date,
            end_at_date=row.end_at_date)
