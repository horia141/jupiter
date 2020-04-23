"""Repository for big plans."""

import logging
import enum
import os.path
import typing
from typing import Final, Any, ClassVar, Dict, Iterable, List, Optional, Tuple, Set
import uuid

import jsonschema as js
import yaml
import pendulum

from repository.common import RefId, RepositoryError


LOGGER = logging.getLogger(__name__)


@enum.unique
class BigPlanStatus(enum.Enum):
    """The status of a big plan."""
    NOT_STARTED = "not-started"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    NOT_DONE = "not-done"
    DONE = "done"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))


@typing.final
class BigPlan:
    """A big plan."""

    _ref_id: RefId
    _project_ref_id: RefId
    _name: str
    _archived: bool
    _status: BigPlanStatus
    _due_date: Optional[pendulum.DateTime]
    _notion_link_uuid: uuid.UUID

    def __init__(
            self, ref_id: RefId, project_ref_id: RefId, name: str, archived: bool, status: BigPlanStatus,
            due_date: Optional[pendulum.DateTime], notion_link_uuid: uuid.UUID) -> None:
        """Constructor."""
        self._ref_id = ref_id
        self._project_ref_id = project_ref_id
        self._name = name
        self._archived = archived
        self._status = status
        self._due_date = due_date
        self._notion_link_uuid = notion_link_uuid

    def set_name(self, name: str) -> None:
        """Change the name of the big plan."""
        self._name = name

    def set_archived(self, archived: bool) -> None:
        """Change the archived status of a big plan."""
        self._archived = archived

    def set_status(self, status: BigPlanStatus) -> None:
        """Change the status of the big plan."""
        self._status = status

    def set_due_date(self, due_date: Optional[pendulum.DateTime]) -> None:
        """Change the due date of the big plan."""
        self._due_date = due_date

    @property
    def ref_id(self) -> RefId:
        """The id of the big plan."""
        return self._ref_id

    @property
    def project_ref_id(self) -> RefId:
        """The id of the project to which the big plan belongs to."""
        return self._project_ref_id

    @property
    def name(self) -> str:
        """The name of the big plan."""
        return self._name

    @property
    def archived(self) -> bool:
        """The archived status of the big plan."""
        return self._archived

    @property
    def status(self) -> BigPlanStatus:
        """The status of the big plan."""
        return self._status

    @property
    def due_date(self) -> Optional[pendulum.DateTime]:
        """The due date of the big plan."""
        return self._due_date

    @property
    def notion_link_uuid(self) -> uuid.UUID:
        """An UUID to use for linking stuff in Notion."""
        return self._notion_link_uuid


@typing.final
class BigPlansRepository:
    """A repository for big plans."""

    _BIG_PLANS_FILE_PATH: Final[ClassVar[str]] = "/data/big-plans.yaml"

    _BIG_PLANS_SCHEMA: Final[ClassVar[Dict[str, Any]]] = {
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
                        "name": {"type": "string"},
                        "archived": {"type": "boolean"},
                        "status": {"type": "string"},
                        "due_date": {"type": "string"}
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

    def initialze(self) -> None:
        """Initialise this repository."""
        if os.path.exists(BigPlansRepository._BIG_PLANS_FILE_PATH):
            return
        self._bulk_save_big_plans((0, []))

    def create_big_plan(
            self, project_ref_id: RefId, name: str, archived: bool, status: BigPlanStatus,
            due_date: Optional[pendulum.DateTime], notion_link_uuid: uuid.UUID) -> BigPlan:
        """Create a big plan."""
        big_plans_next_idx, big_plans = self._bulk_load_big_plans()

        new_big_plan = BigPlan(
            ref_id=RefId(str(big_plans_next_idx)),
            project_ref_id=project_ref_id,
            name=name,
            archived=archived,
            status=status,
            due_date=due_date,
            notion_link_uuid=notion_link_uuid)

        big_plans_next_idx += 1
        big_plans.append(new_big_plan)

        self._bulk_save_big_plans((big_plans_next_idx, big_plans))

        return new_big_plan

    def remove_big_plan_by_id(self, ref_id: RefId) -> None:
        """Remove a big plan."""
        big_plans_next_idx, big_plans = self._bulk_load_big_plans()

        for big_plan in big_plans:
            if big_plan.ref_id == ref_id:
                big_plan.set_archived(True)
                break
        else:
            raise RepositoryError(f"Big plan with id='{ref_id}' does not exist")

        self._bulk_save_big_plans((big_plans_next_idx, big_plans))

    def list_all_big_plans(self, filter_project_ref_id: Optional[Iterable[RefId]] = None) -> Iterable[BigPlan]:
        """Retrieve all the big plans defined."""
        _, big_plans = self._bulk_load_big_plans(
            filter_project_ref_id=frozenset(filter_project_ref_id) if filter_project_ref_id else None)
        return big_plans

    def load_big_plan_by_id(self, ref_id: RefId) -> BigPlan:
        """Retrieve a particular big plan by its id."""
        _, big_plans = self._bulk_load_big_plans()
        found_big_plans = self._find_big_plan_by_id(ref_id, big_plans)
        if not found_big_plans:
            raise RepositoryError(f"Big plan with id='{ref_id}' does not exist")
        return found_big_plans

    def save_big_plan(self, new_big_plan: BigPlan) -> None:
        """Store a particular big plan with all new properties."""
        big_plans_next_idx, big_plans = self._bulk_load_big_plans()

        if not self._find_big_plan_by_id(new_big_plan.ref_id, big_plans):
            raise RepositoryError(f"Big plan with id='{new_big_plan.ref_id}' does not exist")

        new_big_plans = [(rt if rt.ref_id != new_big_plan.ref_id else new_big_plan)
                         for rt in big_plans]
        self._bulk_save_big_plans((big_plans_next_idx, new_big_plans))

    def _bulk_load_big_plans(
            self, filter_project_ref_id: Optional[Set[RefId]] = None) -> Tuple[int, List[BigPlan]]:
        try:
            with open(BigPlansRepository._BIG_PLANS_FILE_PATH, "r") as big_plans_file:
                big_plans_ser = yaml.safe_load(big_plans_file)
                LOGGER.info("Loaded big plans data")

                self._validator(BigPlansRepository._BIG_PLANS_SCHEMA).validate(big_plans_ser)
                LOGGER.info("Checked big plans structure")

                big_plans_next_idx = big_plans_ser["next_idx"]
                big_plans_iter = \
                    (BigPlan(
                        ref_id=RefId(bp["ref_id"]),
                        project_ref_id=RefId(bp["project_ref_id"]),
                        name=bp["name"],
                        archived=bp["archived"],
                        status=BigPlanStatus(bp["status"]),
                        due_date=pendulum.parse(bp["due_date"]) if bp["due_date"] else None,
                        notion_link_uuid=uuid.UUID(bp["notion_link_uuid"]))
                     for bp in big_plans_ser["entries"])
                big_plans = [rt for rt in big_plans_iter
                             if (rt.archived is False)
                             and (filter_project_ref_id is None or rt.project_ref_id in filter_project_ref_id)]

                return big_plans_next_idx, big_plans
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    def _bulk_save_big_plans(self, bulk_data: Tuple[int, Iterable[BigPlan]]) -> None:
        try:
            with open(BigPlansRepository._BIG_PLANS_FILE_PATH, "w") as big_plans_file:
                big_plans_ser = {
                    "next_idx": bulk_data[0],
                    "entries": [{
                        "ref_id": rt.ref_id,
                        "project_ref_id": rt.project_ref_id,
                        "name": rt.name,
                        "archived": rt.archived,
                        "status": rt.status.value,
                        "due_date": rt.due_date.to_datetime_string() if rt.due_date else None,
                        "notion_link_uuid": str(rt.notion_link_uuid)
                    } for rt in bulk_data[1]]
                }

                self._validator(BigPlansRepository._BIG_PLANS_SCHEMA).validate(big_plans_ser)
                LOGGER.info("Checked big plans structure")

                yaml.dump(big_plans_ser, big_plans_file)
                LOGGER.info("Saved big plans tasks")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    @staticmethod
    def _find_big_plan_by_id(ref_id: RefId, big_plans: Iterable[BigPlan]) -> Optional[BigPlan]:
        try:
            return next(bp for bp in big_plans if bp.ref_id == ref_id)
        except StopIteration:
            return None
