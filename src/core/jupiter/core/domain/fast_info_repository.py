"""A query-like repository for scanning information quickly about entities."""
import abc

from jupiter.core.domain.concept.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.concept.chores.chore_name import ChoreName
from jupiter.core.domain.concept.habits.habit_name import HabitName
from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.concept.metrics.metric_name import MetricName
from jupiter.core.domain.concept.persons.person_name import PersonName
from jupiter.core.domain.concept.projects.project_name import ProjectName
from jupiter.core.domain.concept.schedule.schedule_source import ScheduleSource
from jupiter.core.domain.concept.schedule.schedule_stream_color import (
    ScheduleStreamColor,
)
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.concept.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.concept.vacations.vacation_name import VacationName
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import Repository
from jupiter.core.framework.value import CompositeValue, value


@value
class VacationSummary(CompositeValue):
    """Summary information about a vacation."""

    ref_id: EntityId
    name: VacationName


@value
class ScheduleStreamSummary(CompositeValue):
    """Summary information about a schedule stream."""

    ref_id: EntityId
    source: ScheduleSource
    name: ScheduleStreamName
    color: ScheduleStreamColor


@value
class ProjectSummary(CompositeValue):
    """Summary information about a project."""

    ref_id: EntityId
    parent_project_ref_id: EntityId | None
    name: ProjectName
    order_of_child_projects: list[EntityId]


@value
class InboxTaskSummary(CompositeValue):
    """Summary information about an inbox task."""

    ref_id: EntityId
    name: InboxTaskName


@value
class HabitSummary(CompositeValue):
    """Summary information about a habit."""

    ref_id: EntityId
    name: HabitName


@value
class ChoreSummary(CompositeValue):
    """Summary information about a chore."""

    ref_id: EntityId
    name: ChoreName


@value
class BigPlanSummary(CompositeValue):
    """Summary information about a big plan."""

    ref_id: EntityId
    name: BigPlanName
    project_ref_id: EntityId


@value
class SmartListSummary(CompositeValue):
    """Summary information about a smart list."""

    ref_id: EntityId
    name: SmartListName
    icon: EntityIcon | None


@value
class MetricSummary(CompositeValue):
    """Summary information about a metric."""

    ref_id: EntityId
    name: MetricName
    icon: EntityIcon | None


@value
class PersonSummary(CompositeValue):
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
    ) -> list[VacationSummary]:
        """Find all summaries about vacations."""

    @abc.abstractmethod
    async def find_all_schedule_stream_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[ScheduleStreamSummary]:
        """Find all summaries about schedule streams."""

    @abc.abstractmethod
    async def find_all_project_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[ProjectSummary]:
        """Find all summaries about projects."""

    @abc.abstractmethod
    async def find_all_inbox_task_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[InboxTaskSummary]:
        """Find all summaries about inbox tasks."""

    @abc.abstractmethod
    async def find_all_habit_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[HabitSummary]:
        """Find all summaries about habits."""

    @abc.abstractmethod
    async def find_all_chore_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[ChoreSummary]:
        """Find all summaries about chores."""

    @abc.abstractmethod
    async def find_all_big_plan_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[BigPlanSummary]:
        """Find all summaries about big plans."""

    @abc.abstractmethod
    async def find_all_smart_list_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[SmartListSummary]:
        """Find all summaries about smart lists."""

    @abc.abstractmethod
    async def find_all_metric_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[MetricSummary]:
        """Find all summaries about metrics."""

    @abc.abstractmethod
    async def find_all_person_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[PersonSummary]:
        """Find all summaries about persons."""
