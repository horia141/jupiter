"""Domain-level storage interaction."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.domain.big_plans.infra.big_plan_collection_repository import BigPlanCollectionRepository
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.domain.inbox_tasks.infra.inbox_task_collection_repository import InboxTaskCollectionRepository
from jupiter.domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository
from jupiter.domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from jupiter.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.domain.prm.infra.person_repository import PersonRepository
from jupiter.domain.prm.infra.prm_database_repository import PrmDatabaseRepository
from jupiter.domain.projects.infra.project_repository import ProjectRepository
from jupiter.domain.recurring_tasks.infra.recurring_task_collection_repository import RecurringTaskCollectionRepository
from jupiter.domain.recurring_tasks.infra.recurring_task_repository import RecurringTaskRepository
from jupiter.domain.smart_lists.infra.smart_list_item_repository import SmartListItemRepository
from jupiter.domain.smart_lists.infra.smart_list_repository import SmartListRepository
from jupiter.domain.smart_lists.infra.smart_list_tag_repository import SmartListTagRepository
from jupiter.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository


class UnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @property
    @abc.abstractmethod
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace database repository."""

    @property
    @abc.abstractmethod
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""

    @property
    @abc.abstractmethod
    def project_repository(self) -> ProjectRepository:
        """The project database repository."""

    @property
    @abc.abstractmethod
    def inbox_task_collection_repository(self) -> InboxTaskCollectionRepository:
        """The inbox task collection repository."""

    @property
    @abc.abstractmethod
    def inbox_task_repository(self) -> InboxTaskRepository:
        """The inbox task repository."""

    @property
    @abc.abstractmethod
    def recurring_task_collection_repository(self) -> RecurringTaskCollectionRepository:
        """The recurring task collection repository."""

    @property
    @abc.abstractmethod
    def recurring_task_repository(self) -> RecurringTaskRepository:
        """The recurring task repository."""

    @property
    @abc.abstractmethod
    def big_plan_collection_repository(self) -> BigPlanCollectionRepository:
        """The big plan collection repository."""

    @property
    @abc.abstractmethod
    def big_plan_repository(self) -> BigPlanRepository:
        """The big plan repository."""

    @property
    @abc.abstractmethod
    def smart_list_repository(self) -> SmartListRepository:
        """The smart list repository."""

    @property
    @abc.abstractmethod
    def smart_list_tag_repository(self) -> SmartListTagRepository:
        """The smart list tag repository."""

    @property
    @abc.abstractmethod
    def smart_list_item_repository(self) -> SmartListItemRepository:
        """The smart list item repository."""

    @property
    @abc.abstractmethod
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""

    @property
    @abc.abstractmethod
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""

    @property
    @abc.abstractmethod
    def prm_database_repository(self) -> PrmDatabaseRepository:
        """The PRM database repository."""

    @property
    @abc.abstractmethod
    def person_repository(self) -> PersonRepository:
        """The person repository."""


class StorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[UnitOfWork]:
        """Build a unit of work."""
