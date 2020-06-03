"""Repository for big plans."""

from dataclasses import dataclass
import logging
from pathlib import Path
from types import TracebackType
import typing
from typing import Final, ClassVar, Iterable, List, Optional, Type
import uuid

import pendulum

from models.basic import EntityId, BigPlanStatus
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage, JSONDictType

LOGGER = logging.getLogger(__name__)


@dataclass()
class BigPlan:
    """A big plan."""

    ref_id: EntityId
    project_ref_id: EntityId
    name: str
    archived: bool
    status: BigPlanStatus
    due_date: Optional[pendulum.DateTime]
    notion_link_uuid: uuid.UUID


@typing.final
class BigPlansRepository:
    """A repository for big plans."""

    _BIG_PLANS_FILE_PATH: ClassVar[Path] = Path("/data/big-plans.yaml")

    _structured_storage: Final[StructuredCollectionStorage[BigPlan]]

    def __init__(self) -> None:
        """Constructor."""
        self._structured_storage = StructuredCollectionStorage(self._BIG_PLANS_FILE_PATH, self)

    def __enter__(self) -> 'BigPlansRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_big_plan(
            self, project_ref_id: EntityId, name: str, archived: bool, status: BigPlanStatus,
            due_date: Optional[pendulum.DateTime], notion_link_uuid: uuid.UUID) -> BigPlan:
        """Create a big plan."""
        big_plans_next_idx, big_plans = self._structured_storage.load()

        new_big_plan = BigPlan(
            ref_id=EntityId(str(big_plans_next_idx)),
            project_ref_id=project_ref_id,
            name=name,
            archived=archived,
            status=status,
            due_date=due_date,
            notion_link_uuid=notion_link_uuid)

        big_plans_next_idx += 1
        big_plans.append(new_big_plan)

        self._structured_storage.save((big_plans_next_idx, big_plans))

        return new_big_plan

    def archive_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Remove a big plan."""
        big_plans_next_idx, big_plans = self._structured_storage.load()

        for big_plan in big_plans:
            if big_plan.ref_id == ref_id:
                big_plan.archived = True
                self._structured_storage.save((big_plans_next_idx, big_plans))
                return big_plan

        raise RepositoryError(f"Big plan with id='{ref_id}' does not exist")

    def load_all_big_plans(
            self,
            filter_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlan]:
        """Retrieve all the big plans defined."""
        _, big_plans = self._structured_storage.load()
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else []
        filter_project_ref_id_set = frozenset(filter_project_ref_ids) if filter_project_ref_ids else []
        return [bp for bp in big_plans
                if (filter_archived is False or bp.archived is False)
                and (len(filter_ref_ids_set) == 0 or bp.ref_id in filter_ref_ids_set)
                and (len(filter_project_ref_id_set) == 0 or bp.project_ref_id in filter_project_ref_id_set)]

    def load_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Retrieve a particular big plan by its id."""
        _, big_plans = self._structured_storage.load()
        found_big_plans = self._find_big_plan_by_id(ref_id, big_plans)
        if not found_big_plans:
            raise RepositoryError(f"Big plan with id='{ref_id}' does not exist")
        if found_big_plans.archived:
            raise RepositoryError(f"Big plan with id='{ref_id}' is archived")
        return found_big_plans

    def save_big_plan(self, new_big_plan: BigPlan) -> BigPlan:
        """Store a particular big plan with all new properties."""
        big_plans_next_idx, big_plans = self._structured_storage.load()

        if not self._find_big_plan_by_id(new_big_plan.ref_id, big_plans):
            raise RepositoryError(f"Big plan with id='{new_big_plan.ref_id}' does not exist")

        new_big_plans = [(rt if rt.ref_id != new_big_plan.ref_id else new_big_plan)
                         for rt in big_plans]
        self._structured_storage.save((big_plans_next_idx, new_big_plans))

        return new_big_plan

    def hard_remove_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Hard remove a big plan."""
        big_plans_next_idx, big_plans = self._structured_storage.load()
        found_big_plan = self._find_big_plan_by_id(ref_id, big_plans)
        if not found_big_plan:
            raise RepositoryError(f"Big plan with id='{ref_id}' does not exist")
        new_big_plans = [it for it in big_plans if it.ref_id != ref_id]
        self._structured_storage.save((big_plans_next_idx, new_big_plans))
        return found_big_plan

    @staticmethod
    def _find_big_plan_by_id(ref_id: EntityId, big_plans: List[BigPlan]) -> Optional[BigPlan]:
        try:
            return next(bp for bp in big_plans if bp.ref_id == ref_id)
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
                "name": {"type": "string"},
                "archived": {"type": "boolean"},
                "status": {"type": "string"},
                "due_date": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> BigPlan:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return BigPlan(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            name=typing.cast(str, storage_form["name"]),
            archived=typing.cast(bool, storage_form["archived"]),
            status=BigPlanStatus(typing.cast(str, storage_form["status"])),
            due_date=pendulum.parse(typing.cast(str, storage_form["due_date"])) if storage_form["due_date"] else None,
            notion_link_uuid=uuid.UUID(typing.cast(str, storage_form["notion_link_uuid"])))

    @staticmethod
    def live_to_storage(live_form: BigPlan) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "project_ref_id": live_form.project_ref_id,
            "name": live_form.name,
            "archived": live_form.archived,
            "status": live_form.status.value,
            "due_date": live_form.due_date.to_datetime_string() if live_form.due_date else None,
            "notion_link_uuid": str(live_form.notion_link_uuid)
        }
