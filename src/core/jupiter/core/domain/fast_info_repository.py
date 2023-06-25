"""A query-like repository for scanning information quickly about entities."""
import abc
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import Repository
from jupiter.core.framework.value import Value


@dataclass
class VacationSummary(Value):
    """Summary information about a vacation."""

    ref_id: EntityId
    name: VacationName


@dataclass
class ProjectSummary(Value):
    """Summary information about a project."""

    ref_id: EntityId
    name: ProjectName


@dataclass
class InboxTaskSummary(Value):
    """Summary information about an inbox task."""

    ref_id: EntityId
    name: InboxTaskName


@dataclass
class HabitSummary(Value):
    """Summary information about a habit."""

    ref_id: EntityId
    name: HabitName


@dataclass
class ChoreSummary(Value):
    """Summary information about a chore."""

    ref_id: EntityId
    name: ChoreName


@dataclass
class BigPlanSummary(Value):
    """Summary information about a big plan."""

    ref_id: EntityId
    name: BigPlanName
    project_ref_id: EntityId


@dataclass
class SmartListSummary(Value):
    """Summary information about a smart list."""

    ref_id: EntityId
    name: SmartListName
    icon: Optional[EntityIcon] = None


@dataclass
class MetricSummary(Value):
    """Summary information about a metric."""

    ref_id: EntityId
    name: MetricName
    icon: Optional[EntityIcon] = None


@dataclass
class PersonSummary(Value):
    """Summary information about a person."""

    ref_id: EntityId
    name: PersonName


class FastInfoRepository(Repository, abc.ABC):
    """A query-like repository for scanning information quickly about entities."""

    @abc.abstractmethod
    async def find_all_vacation_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[VacationSummary]:
        """Find all summaries about vacations."""

    @abc.abstractmethod
    async def find_all_project_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[ProjectSummary]:
        """Find all summaries about projects."""

    @abc.abstractmethod
    async def find_all_inbox_task_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[InboxTaskSummary]:
        """Find all summaries about inbox tasks."""

    @abc.abstractmethod
    async def find_all_habit_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[HabitSummary]:
        """Find all summaries about habits."""

    @abc.abstractmethod
    async def find_all_chore_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[ChoreSummary]:
        """Find all summaries about chores."""

    @abc.abstractmethod
    async def find_all_big_plan_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[BigPlanSummary]:
        """Find all summaries about big plans."""

    @abc.abstractmethod
    async def find_all_smart_list_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[SmartListSummary]:
        """Find all summaries about smart lists."""

    @abc.abstractmethod
    async def find_all_metric_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[MetricSummary]:
        """Find all summaries about metrics."""

    @abc.abstractmethod
    async def find_all_person_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[PersonSummary]:
        """Find all summaries about persons."""
