"""Repository for big plans."""
from dataclasses import dataclass
import logging
from pathlib import Path
from types import TracebackType
import typing
from typing import Final, ClassVar, Iterable, Optional, Type
import uuid

from models.basic import BigPlanStatus, ADate, BasicValidator, Timestamp
from models.framework import EntityId, JSONDictType
from utils.storage import BaseEntityRow, EntitiesStorage, In
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class BigPlanRow(BaseEntityRow):
    """A big plan."""

    project_ref_id: EntityId
    name: str
    status: BigPlanStatus
    due_date: Optional[ADate]
    notion_link_uuid: uuid.UUID
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


@typing.final
class BigPlansRepository:
    """A repository for big plans."""

    _BIG_PLANS_FILE_PATH: ClassVar[Path] = Path("./big-plans")
    _BIG_PLANS_NUM_SHARDS: ClassVar[int] = 10

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[BigPlanRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[BigPlanRow](
            self._BIG_PLANS_FILE_PATH, self._BIG_PLANS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'BigPlansRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_big_plan(
            self, project_ref_id: EntityId, name: str, archived: bool, status: BigPlanStatus,
            due_date: Optional[ADate], notion_link_uuid: uuid.UUID) -> BigPlanRow:
        """Create a big plan."""
        new_big_plan_row = BigPlanRow(
            project_ref_id=project_ref_id,
            name=name,
            archived=archived,
            status=status,
            due_date=due_date,
            notion_link_uuid=notion_link_uuid,
            accepted_time=self._time_provider.get_current_time() if status.is_accepted_or_more else None,
            working_time=self._time_provider.get_current_time() if status.is_working_or_more else None,
            completed_time=self._time_provider.get_current_time() if status.is_completed else None)

        return self._storage.create(new_big_plan_row)

    def archive_big_plan(self, ref_id: EntityId) -> BigPlanRow:
        """Remove a big plan."""
        return self._storage.archive(ref_id)

    def remove_big_plan(self, ref_id: EntityId) -> BigPlanRow:
        """Hard remove a big plan."""
        return self._storage.remove(ref_id)

    def update_big_plan(
            self, new_big_plan_row: BigPlanRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            accepted_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            working_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING,
            completed_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> BigPlanRow:
        """Store a particular big plan with all new properties."""
        accepted_time_action.act(new_big_plan_row, "accepted_time", self._time_provider.get_current_time())
        working_time_action.act(new_big_plan_row, "working_time", self._time_provider.get_current_time())
        completed_time_action.act(new_big_plan_row, "completed_time", self._time_provider.get_current_time())
        return self._storage.update(new_big_plan_row, archived_time_action=archived_time_action)

    def load_big_plan(self, ref_id: EntityId, allow_archived: bool = False) -> BigPlanRow:
        """Retrieve a particular big plan by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_big_plans(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlanRow]:
        """Retrieve all the big plans defined."""
        return self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(*filter_project_ref_ids) if filter_project_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"},
            "name": {"type": "string"},
            "status": {"type": "string"},
            "due_date": {"type": ["string", "null"]},
            "accepted_time": {"type": ["string", "null"]},
            "working_time": {"type": ["string", "null"]},
            "completed_time": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> BigPlanRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return BigPlanRow(
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            name=typing.cast(str, storage_form["name"]),
            archived=typing.cast(bool, storage_form["archived"]),
            status=BigPlanStatus(typing.cast(str, storage_form["status"])),
            due_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["due_date"]))
            if storage_form["due_date"] else None,
            notion_link_uuid=uuid.UUID(typing.cast(str, storage_form["notion_link_uuid"])),
            accepted_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["accepted_time"]))
            if storage_form["accepted_time"] else None,
            working_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["working_time"]))
            if storage_form["working_time"] else None,
            completed_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["completed_time"]))
            if storage_form["completed_time"] else None)

    @staticmethod
    def live_to_storage(live_form: BigPlanRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": str(live_form.project_ref_id),
            "name": live_form.name,
            "status": live_form.status.value,
            "due_date": BasicValidator.adate_to_str(live_form.due_date) if live_form.due_date else None,
            "notion_link_uuid": str(live_form.notion_link_uuid),
            "accepted_time": BasicValidator.timestamp_to_str(live_form.accepted_time)
                             if live_form.accepted_time else None,
            "working_time": BasicValidator.timestamp_to_str(live_form.working_time)
                            if live_form.working_time else None,
            "completed_time": BasicValidator.timestamp_to_str(live_form.completed_time)
                              if live_form.completed_time else None
        }
