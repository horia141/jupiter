"""Domain-level storage interaction."""
import abc
from typing import AsyncContextManager

from jupiter.core.domain.auth.infra.auth_repository import AuthRepository
from jupiter.core.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.core.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.core.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionRepository,
)
from jupiter.core.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.core.domain.fast_info_repository import FastInfoRepository
from jupiter.core.domain.habits.infra.habit_collection_repository import (
    HabitCollectionRepository,
)
from jupiter.core.domain.habits.infra.habit_repository import HabitRepository
from jupiter.core.domain.inbox_tasks.infra.inbox_task_collection_repository import (
    InboxTaskCollectionRepository,
)
from jupiter.core.domain.inbox_tasks.infra.inbox_task_repository import (
    InboxTaskRepository,
)
from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import PersonRepository
from jupiter.core.domain.projects.infra.project_collection_repository import (
    ProjectCollectionRepository,
)
from jupiter.core.domain.projects.infra.project_repository import ProjectRepository
from jupiter.core.domain.push_integrations.email.infra.email_task_collection_repository import (
    EmailTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_repository import (
    EmailTaskRepository,
)
from jupiter.core.domain.push_integrations.group.infra.push_integration_group_repository import (
    PushIntegrationGroupRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
)
from jupiter.core.domain.search_repository import SearchRepository
from jupiter.core.domain.smart_lists.infra.smart_list_collection_repository import (
    SmartListCollectionRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_item_repository import (
    SmartListItemRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_repository import (
    SmartListRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_tag_repository import (
    SmartListTagRepository,
)
from jupiter.core.domain.user.infra.user_repository import UserRepository
from jupiter.core.domain.user_workspace_link.infra.user_workspace_link_repository import (
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionRepository,
)
from jupiter.core.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceRepository,
)


class DomainUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @property
    @abc.abstractmethod
    def user_repository(self) -> UserRepository:
        """The user repository."""

    @property
    @abc.abstractmethod
    def auth_repository(self) -> AuthRepository:
        """The auth repository."""

    @property
    @abc.abstractmethod
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace repository."""

    @property
    @abc.abstractmethod
    def user_workspace_link_repository(self) -> UserWorkspaceLinkRepository:
        """The user workspace link repository."""

    @property
    @abc.abstractmethod
    def vacation_collection_repository(self) -> VacationCollectionRepository:
        """The vacation collection repository."""

    @property
    @abc.abstractmethod
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""

    @property
    @abc.abstractmethod
    def project_collection_repository(self) -> ProjectCollectionRepository:
        """The project collection repository."""

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
    def habit_collection_repository(self) -> HabitCollectionRepository:
        """The habit collection repository."""

    @property
    @abc.abstractmethod
    def habit_repository(self) -> HabitRepository:
        """The habit repository."""

    @property
    @abc.abstractmethod
    def chore_collection_repository(self) -> ChoreCollectionRepository:
        """The chore collection repository."""

    @property
    @abc.abstractmethod
    def chore_repository(self) -> ChoreRepository:
        """The chore repository."""

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
    def smart_list_collection_repository(self) -> SmartListCollectionRepository:
        """The smart list collection repository."""

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
    def metric_collection_repository(self) -> MetricCollectionRepository:
        """The metric collection repository."""

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
    def person_collection_repository(self) -> PersonCollectionRepository:
        """The person collection repository."""

    @property
    @abc.abstractmethod
    def person_repository(self) -> PersonRepository:
        """The person repository."""

    @property
    @abc.abstractmethod
    def push_integration_group_repository(self) -> PushIntegrationGroupRepository:
        """The push integration group repository."""

    @property
    @abc.abstractmethod
    def slack_task_collection_repository(self) -> SlackTaskCollectionRepository:
        """The Slack task collection repository."""

    @property
    @abc.abstractmethod
    def slack_task_repository(self) -> SlackTaskRepository:
        """The Slack task repository."""

    @property
    @abc.abstractmethod
    def email_task_collection_repository(self) -> EmailTaskCollectionRepository:
        """The email task collection repository."""

    @property
    @abc.abstractmethod
    def email_task_repository(self) -> EmailTaskRepository:
        """The email task repository."""

    @property
    @abc.abstractmethod
    def fast_into_repository(self) -> FastInfoRepository:
        """The fast info repository."""


class DomainStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AsyncContextManager[DomainUnitOfWork]:
        """Build a unit of work."""


class SearchUnitOfWork(abc.ABC):
    """A unit of work from a search engine."""

    @property
    @abc.abstractmethod
    def search_repository(self) -> SearchRepository:
        """The search repostory."""


class SearchStorageEngine(abc.ABC):
    """A storage engine of some form for the search engine."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AsyncContextManager[SearchUnitOfWork]:
        """Build a unit of work."""
