"""Repository for big plans."""
import logging
import typing
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, Optional, Type

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_collection_repository import BigPlanCollectionRepository, \
    BigPlanCollectionAlreadyExistsError, BigPlanCollectionNotFoundError
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository, BigPlanNotFoundError
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.repository.yaml.infra.storage import BaseEntityRow, EntitiesStorage, In, Eq, StorageEntityNotFoundError
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _BigPlanCollectionRow(BaseEntityRow):
    """A container for big plans."""
    project_ref_id: EntityId


class YamlBigPlanCollectionRepository(BigPlanCollectionRepository):
    """A repository for big plan collections."""

    _INBOX_TASK_COLLECTIONS_FILE_PATH: ClassVar[Path] = Path("./big-plan-collections")
    _INBOX_TASK_COLLECTIONS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_BigPlanCollectionRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_BigPlanCollectionRow](
            self._INBOX_TASK_COLLECTIONS_FILE_PATH, self._INBOX_TASK_COLLECTIONS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlBigPlanCollectionRepository':
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

    def create(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Create a big plan collection."""
        big_plan_collection_rows = \
            self._storage.find_all(allow_archived=True, project_ref_id=Eq(big_plan_collection.project_ref_id))

        if len(big_plan_collection_rows) > 0:
            raise BigPlanCollectionAlreadyExistsError(
                f"Big plan collection for project ='{big_plan_collection.project_ref_id}' already exists")

        new_big_plan_collection_row = self._storage.create(_BigPlanCollectionRow(
            archived=big_plan_collection.archived,
            project_ref_id=big_plan_collection.project_ref_id))
        big_plan_collection.assign_ref_id(new_big_plan_collection_row.ref_id)
        return big_plan_collection

    def save(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Create a big plan collection."""
        try:
            return self._row_to_entity(self._storage.update(self._entity_to_row(big_plan_collection)))
        except StorageEntityNotFoundError as err:
            raise BigPlanCollectionNotFoundError(
                f"Big plan task collection with id {big_plan_collection.ref_id} does not exist") from err

    def load_by_id(self, ref_id: EntityId) -> BigPlanCollection:
        """Load an inbox task collection by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=False))
        except StorageEntityNotFoundError as err:
            raise BigPlanCollectionNotFoundError(f"Big plan task collection with id {ref_id} does not exist") from err

    def load_by_project(self, project_ref_id: EntityId) -> BigPlanCollection:
        """Find an big plan collection by project ref id."""
        try:
            big_plan_collection_row = \
                self._storage.find_first(allow_archived=False, project_ref_id=Eq(project_ref_id))
        except StorageEntityNotFoundError as err:
            raise BigPlanCollectionNotFoundError(
                f"Big plan collection for project = '{project_ref_id}' was not found") from err
        return self._row_to_entity(big_plan_collection_row)

    def find_all(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlanCollection]:
        """Retrieve inbox task collections."""
        return [self._row_to_entity(itr) for itr in self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(
                *filter_project_ref_ids) if filter_project_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> BigPlanCollection:
        """Hard remove an big plan collection - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id=ref_id))
        except StorageEntityNotFoundError as err:
            raise BigPlanCollectionNotFoundError(
                f"Big plan collection with id = '{ref_id}' was not found") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _BigPlanCollectionRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _BigPlanCollectionRow(
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _BigPlanCollectionRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": str(live_form.project_ref_id)
        }

    @staticmethod
    def _entity_to_row(big_plan_collection: BigPlanCollection) -> _BigPlanCollectionRow:
        big_plan_collection_row = _BigPlanCollectionRow(
            archived=big_plan_collection.archived,
            project_ref_id=big_plan_collection.project_ref_id)
        big_plan_collection_row.ref_id = big_plan_collection.ref_id
        big_plan_collection_row.created_time = big_plan_collection.created_time
        big_plan_collection_row.archived_time = big_plan_collection.archived_time
        big_plan_collection_row.last_modified_time = big_plan_collection.last_modified_time
        return big_plan_collection_row

    @staticmethod
    def _row_to_entity(row: _BigPlanCollectionRow) -> BigPlanCollection:
        return BigPlanCollection(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            project_ref_id=row.project_ref_id)


@dataclass()
class _BigPlanRow(BaseEntityRow):
    """A big plan."""

    big_plan_collection_ref_id: EntityId
    name: BigPlanName
    status: BigPlanStatus
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    notion_link_uuid: uuid.UUID
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


@typing.final
class YamlBigPlanRepository(BigPlanRepository):
    """A repository for big plans."""

    _BIG_PLANS_FILE_PATH: ClassVar[Path] = Path("./big-plans")
    _BIG_PLANS_NUM_SHARDS: ClassVar[int] = 10

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[_BigPlanRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[_BigPlanRow](
            self._BIG_PLANS_FILE_PATH, self._BIG_PLANS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlBigPlanRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, big_plan_collection: BigPlanCollection, big_plan: BigPlan) -> BigPlan:
        """Create a big plan."""
        new_big_plan_row = self._storage.create(_BigPlanRow(
            big_plan_collection_ref_id=big_plan_collection.ref_id,
            name=big_plan.name,
            archived=big_plan.archived,
            status=big_plan.status,
            actionable_date=big_plan.actionable_date,
            due_date=big_plan.due_date,
            notion_link_uuid=big_plan.notion_link_uuid,
            accepted_time=big_plan.accepted_time,
            working_time=big_plan.working_time,
            completed_time=big_plan.completed_time))
        big_plan.assign_ref_id(new_big_plan_row.ref_id)
        return big_plan

    def save(self, big_plan: BigPlan) -> BigPlan:
        """Save a big plan - it should already exist."""
        big_plan_row = self._entity_to_row(big_plan)
        try:
            big_plan_row = self._storage.update(big_plan_row)
        except StorageEntityNotFoundError as err:
            raise BigPlanNotFoundError(f"Big plan with id {big_plan.ref_id} was not found") from err
        return self._row_to_entity(big_plan_row)

    def dump_all(self, big_plan: Iterable[BigPlan]) -> None:
        """Save all inbox tasks - good for migrations."""
        self._storage.dump_all(self._entity_to_row(it) for it in big_plan)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BigPlan:
        """Load a big plan by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))
        except StorageEntityNotFoundError as err:
            raise BigPlanNotFoundError(f"Big plan with id {ref_id} was not found") from err

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_big_plan_collection_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlan]:
        """Find all big plans."""
        return [self._row_to_entity(bpr) for bpr in self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            big_plan_collection_ref_id=In(*filter_big_plan_collection_ref_ids)
            if filter_big_plan_collection_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> BigPlan:
        """Hard remove a big plan - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id))
        except StorageEntityNotFoundError as err:
            raise BigPlanNotFoundError(f"Big plan with id {ref_id} was not found") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "big_plan_collection_ref_id": {"type": "string"},
            "name": {"type": "string"},
            "status": {"type": "string"},
            "actionable_date": {"type": ["string", "null"]},
            "due_date": {"type": ["string", "null"]},
            "accepted_time": {"type": ["string", "null"]},
            "working_time": {"type": ["string", "null"]},
            "completed_time": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _BigPlanRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _BigPlanRow(
            big_plan_collection_ref_id=EntityId(typing.cast(str, storage_form["big_plan_collection_ref_id"])),
            name=BigPlanName.from_raw(typing.cast(str, storage_form["name"])),
            archived=typing.cast(bool, storage_form["archived"]),
            status=BigPlanStatus(typing.cast(str, storage_form["status"])),
            actionable_date=ADate.from_str(typing.cast(str, storage_form["actionable_date"]))
            if storage_form["actionable_date"] else None,
            due_date=ADate.from_str(typing.cast(str, storage_form["due_date"]))
            if storage_form["due_date"] else None,
            notion_link_uuid=uuid.UUID(typing.cast(str, storage_form["notion_link_uuid"])),
            accepted_time=Timestamp.from_str(typing.cast(str, storage_form["accepted_time"]))
            if storage_form["accepted_time"] else None,
            working_time=Timestamp.from_str(typing.cast(str, storage_form["working_time"]))
            if storage_form["working_time"] else None,
            completed_time=Timestamp.from_str(typing.cast(str, storage_form["completed_time"]))
            if storage_form["completed_time"] else None)

    @staticmethod
    def live_to_storage(live_form: _BigPlanRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "big_plan_collection_ref_id": str(live_form.big_plan_collection_ref_id),
            "name": str(live_form.name),
            "status": live_form.status.value,
            "actionable_date": str(live_form.actionable_date) if live_form.actionable_date else None,
            "due_date": str(live_form.due_date) if live_form.due_date else None,
            "notion_link_uuid": str(live_form.notion_link_uuid),
            "accepted_time": str(live_form.accepted_time)
                             if live_form.accepted_time else None,
            "working_time": str(live_form.working_time)
                            if live_form.working_time else None,
            "completed_time": str(live_form.completed_time)
                              if live_form.completed_time else None
        }

    @staticmethod
    def _entity_to_row(big_plan: BigPlan) -> _BigPlanRow:
        big_plan_row = _BigPlanRow(
            big_plan_collection_ref_id=big_plan.big_plan_collection_ref_id,
            name=big_plan.name,
            archived=big_plan.archived,
            status=big_plan.status,
            actionable_date=big_plan.actionable_date,
            due_date=big_plan.due_date,
            notion_link_uuid=big_plan.notion_link_uuid,
            accepted_time=big_plan.accepted_time,
            working_time=big_plan.working_time,
            completed_time=big_plan.completed_time)
        big_plan_row.ref_id = big_plan.ref_id
        big_plan_row.created_time = big_plan.created_time
        big_plan_row.archived_time = big_plan.archived_time
        big_plan_row.last_modified_time = big_plan.last_modified_time
        return big_plan_row

    @staticmethod
    def _row_to_entity(row: _BigPlanRow) -> BigPlan:
        return BigPlan(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            big_plan_collection_ref_id=row.big_plan_collection_ref_id,
            name=row.name,
            status=row.status,
            actionable_date=row.actionable_date,
            due_date=row.due_date,
            notion_link_uuid=row.notion_link_uuid,
            accepted_time=row.accepted_time,
            working_time=row.working_time,
            completed_time=row.completed_time)
