"""The real implementation of an engine."""
import typing
from contextlib import contextmanager
from types import TracebackType
from typing import Final, Iterator, Optional, Type

from sqlalchemy import MetaData
from sqlalchemy.future import Engine

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionRepository,
)
from jupiter.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.domain.habits.infra.habit_collection_repository import (
    HabitCollectionRepository,
)
from jupiter.domain.habits.infra.habit_repository import HabitRepository
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.infra.inbox_task_collection_repository import (
    InboxTaskCollectionRepository,
)
from jupiter.domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository
from jupiter.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from jupiter.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.domain.persons.infra.person_repository import PersonRepository
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.domain.projects.infra.project_collection_repository import (
    ProjectCollectionRepository,
)
from jupiter.domain.projects.infra.project_repository import ProjectRepository
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.domain.push_integrations.group.infra.push_integration_group_repository import (
    PushIntegrationGroupRepository,
)
from jupiter.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
)
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.domain.remote.notion.connection_repository import (
    NotionConnectionRepository,
)
from jupiter.domain.smart_lists.infra.smart_list_collection_repository import (
    SmartListCollectionRepository,
)
from jupiter.domain.smart_lists.infra.smart_list_item_repository import (
    SmartListItemRepository,
)
from jupiter.domain.smart_lists.infra.smart_list_repository import SmartListRepository
from jupiter.domain.smart_lists.infra.smart_list_tag_repository import (
    SmartListTagRepository,
)
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.storage_engine import (
    DomainUnitOfWork,
    DomainStorageEngine,
    LeafT,
    TrunkT,
    BranchT,
    BranchEntityKeyT,
)
from jupiter.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionRepository,
)
from jupiter.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository
from jupiter.framework.repository import (
    LeafEntityRepository,
    TrunkEntityRepository,
    BranchEntityRepository,
)
from jupiter.repository.sqlite.connection import SqliteConnection
from jupiter.repository.sqlite.domain.big_plans import (
    SqliteBigPlanCollectionRepository,
    SqliteBigPlanRepository,
)
from jupiter.repository.sqlite.domain.chores import (
    SqliteChoreCollectionRepository,
    SqliteChoreRepository,
)
from jupiter.repository.sqlite.domain.habits import (
    SqliteHabitCollectionRepository,
    SqliteHabitRepository,
)
from jupiter.repository.sqlite.domain.inbox_tasks import (
    SqliteInboxTaskCollectionRepository,
    SqliteInboxTaskRepository,
)
from jupiter.repository.sqlite.domain.metrics import (
    SqliteMetricRepository,
    SqliteMetricEntryRepository,
    SqliteMetricCollectionRepository,
)
from jupiter.repository.sqlite.domain.persons import (
    SqlitePersonCollectionRepository,
    SqlitePersonRepository,
)
from jupiter.repository.sqlite.domain.projects import (
    SqliteProjectRepository,
    SqliteProjectCollectionRepository,
)
from jupiter.repository.sqlite.domain.push_integration.push_integration_groups import (
    SqlitePushIntegrationGroupRepository,
)
from jupiter.repository.sqlite.domain.push_integration.slack_tasks import (
    SqliteSlackTaskCollectionRepository,
    SqliteSlackTaskRepository,
)
from jupiter.repository.sqlite.domain.remote.notion.connections import (
    SqliteNotionConnectionRepository,
)
from jupiter.repository.sqlite.domain.smart_lists import (
    SqliteSmartListRepository,
    SqliteSmartListTagRepository,
    SqliteSmartListItemRepository,
    SqliteSmartListCollectionRepository,
)
from jupiter.repository.sqlite.domain.vacations import (
    SqliteVacationRepository,
    SqliteVacationCollectionRepository,
)
from jupiter.repository.sqlite.domain.workspace import SqliteWorkspaceRepository


class SqliteDomainUnitOfWork(DomainUnitOfWork):
    """A Sqlite specific metric unit of work."""

    _workspace_repository: Final[SqliteWorkspaceRepository]
    _vacation_collection_repository: Final[SqliteVacationCollectionRepository]
    _vacation_repository: Final[SqliteVacationRepository]
    _project_collection_repository: Final[SqliteProjectCollectionRepository]
    _project_repository: Final[SqliteProjectRepository]
    _inbox_task_collection_repository: Final[SqliteInboxTaskCollectionRepository]
    _inbox_task_repository: Final[SqliteInboxTaskRepository]
    _habit_collection_repository: Final[SqliteHabitCollectionRepository]
    _habit_repository: Final[SqliteHabitRepository]
    _chore_collection_repository: Final[SqliteChoreCollectionRepository]
    _chore_repository: Final[SqliteChoreRepository]
    _big_plan_collection_repository: Final[SqliteBigPlanCollectionRepository]
    _big_plan_repository: Final[SqliteBigPlanRepository]
    _smart_list_collection_repository: Final[SmartListCollectionRepository]
    _smart_list_repository: Final[SqliteSmartListRepository]
    _smart_list_tag_reposiotry: Final[SqliteSmartListTagRepository]
    _smart_list_item_repository: Final[SqliteSmartListItemRepository]
    _metric_collection_repository: Final[SqliteMetricCollectionRepository]
    _metric_repository: Final[SqliteMetricRepository]
    _metric_entry_repository: Final[SqliteMetricEntryRepository]
    _person_collection_repository: Final[SqlitePersonCollectionRepository]
    _person_repository: Final[SqlitePersonRepository]
    _push_integration_group_repository: Final[SqlitePushIntegrationGroupRepository]
    _slack_task_collection_repository: Final[SqliteSlackTaskCollectionRepository]
    _slack_task_repository: Final[SqliteSlackTaskRepository]
    _notion_connection_repository: Final[SqliteNotionConnectionRepository]

    def __init__(
        self,
        workspace_repository: SqliteWorkspaceRepository,
        vacation_repository: SqliteVacationRepository,
        vacation_collection_repository: SqliteVacationCollectionRepository,
        project_collection_repository: SqliteProjectCollectionRepository,
        project_repository: SqliteProjectRepository,
        inbox_task_collection_repository: SqliteInboxTaskCollectionRepository,
        inbox_task_repository: SqliteInboxTaskRepository,
        habit_collection_repository: SqliteHabitCollectionRepository,
        habit_repository: SqliteHabitRepository,
        chore_collection_repository: SqliteChoreCollectionRepository,
        chore_repository: SqliteChoreRepository,
        big_plan_collection_repository: SqliteBigPlanCollectionRepository,
        big_plan_repository: SqliteBigPlanRepository,
        smart_list_collection_repository: SqliteSmartListCollectionRepository,
        smart_list_repository: SqliteSmartListRepository,
        smart_list_tag_repository: SqliteSmartListTagRepository,
        smart_list_item_repository: SqliteSmartListItemRepository,
        metric_collection_repository: SqliteMetricCollectionRepository,
        metric_repository: SqliteMetricRepository,
        metric_entry_repository: SqliteMetricEntryRepository,
        person_collection_repository: SqlitePersonCollectionRepository,
        person_repository: SqlitePersonRepository,
        push_integration_group_repository: SqlitePushIntegrationGroupRepository,
        slack_task_collection_repository: SqliteSlackTaskCollectionRepository,
        slack_task_repository: SqliteSlackTaskRepository,
        notion_connection_repository: SqliteNotionConnectionRepository,
    ) -> None:
        """Constructor."""
        self._workspace_repository = workspace_repository
        self._vacation_collection_repository = vacation_collection_repository
        self._vacation_repository = vacation_repository
        self._project_collection_repository = project_collection_repository
        self._project_repository = project_repository
        self._inbox_task_collection_repository = inbox_task_collection_repository
        self._inbox_task_repository = inbox_task_repository
        self._habit_collection_repository = habit_collection_repository
        self._habit_repository = habit_repository
        self._chore_collection_repository = chore_collection_repository
        self._chore_repository = chore_repository
        self._big_plan_collection_repository = big_plan_collection_repository
        self._big_plan_repository = big_plan_repository
        self._smart_list_collection_repository = smart_list_collection_repository
        self._smart_list_repository = smart_list_repository
        self._smart_list_tag_reposiotry = smart_list_tag_repository
        self._smart_list_item_repository = smart_list_item_repository
        self._metric_collection_repository = metric_collection_repository
        self._metric_repository = metric_repository
        self._metric_entry_repository = metric_entry_repository
        self._person_collection_repository = person_collection_repository
        self._person_repository = person_repository
        self._push_integration_group_repository = push_integration_group_repository
        self._slack_task_collection_repository = slack_task_collection_repository
        self._slack_task_repository = slack_task_repository
        self._notion_connection_repository = notion_connection_repository

    def __enter__(self) -> "SqliteDomainUnitOfWork":
        """Enter the context."""
        return self

    def __exit__(
        self,
        _exc_type: Optional[typing.Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context."""

    @property
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace repository."""
        return self._workspace_repository

    @property
    def vacation_collection_repository(self) -> VacationCollectionRepository:
        """The vacation collection repository."""
        return self._vacation_collection_repository

    @property
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""
        return self._vacation_repository

    @property
    def project_collection_repository(self) -> ProjectCollectionRepository:
        """The projects repository."""
        return self._project_collection_repository

    @property
    def project_repository(self) -> ProjectRepository:
        """The projects repository."""
        return self._project_repository

    @property
    def inbox_task_collection_repository(self) -> InboxTaskCollectionRepository:
        """The inbox task collection repository."""
        return self._inbox_task_collection_repository

    @property
    def inbox_task_repository(self) -> InboxTaskRepository:
        """The inbox task repository."""
        return self._inbox_task_repository

    @property
    def habit_collection_repository(self) -> HabitCollectionRepository:
        """The habit collection repository."""
        return self._habit_collection_repository

    @property
    def habit_repository(self) -> HabitRepository:
        """The habit repository."""
        return self._habit_repository

    @property
    def chore_collection_repository(self) -> ChoreCollectionRepository:
        """The chore collection repository."""
        return self._chore_collection_repository

    @property
    def chore_repository(self) -> ChoreRepository:
        """The chore repository."""
        return self._chore_repository

    @property
    def big_plan_collection_repository(self) -> BigPlanCollectionRepository:
        """The big plan collection repository."""
        return self._big_plan_collection_repository

    @property
    def big_plan_repository(self) -> BigPlanRepository:
        """The big plan repository."""
        return self._big_plan_repository

    @property
    def smart_list_collection_repository(self) -> SmartListCollectionRepository:
        """The smart list collection repository."""
        return self._smart_list_collection_repository

    @property
    def smart_list_repository(self) -> SmartListRepository:
        """The smart list repository."""
        return self._smart_list_repository

    @property
    def smart_list_tag_repository(self) -> SmartListTagRepository:
        """The smart list tag repository."""
        return self._smart_list_tag_reposiotry

    @property
    def smart_list_item_repository(self) -> SmartListItemRepository:
        """The smart list item repository."""
        return self._smart_list_item_repository

    @property
    def metric_collection_repository(self) -> MetricCollectionRepository:
        """The metric collection repository."""
        return self._metric_collection_repository

    @property
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""
        return self._metric_repository

    @property
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""
        return self._metric_entry_repository

    @property
    def person_collection_repository(self) -> PersonCollectionRepository:
        """The person collection repository."""
        return self._person_collection_repository

    @property
    def person_repository(self) -> PersonRepository:
        """The person repository."""
        return self._person_repository

    @property
    def push_integration_group_repository(self) -> PushIntegrationGroupRepository:
        """The push integration group repository."""
        return self._push_integration_group_repository

    @property
    def slack_task_collection_repository(self) -> SlackTaskCollectionRepository:
        """The Slack task collection repository."""
        return self._slack_task_collection_repository

    @property
    def slack_task_repository(self) -> SlackTaskRepository:
        """The Slack task repository."""
        return self._slack_task_repository

    @property
    def notion_connection_repository(self) -> NotionConnectionRepository:
        """The Notion connection repository."""
        return self._notion_connection_repository

    def get_trunk_repository_for(
        self, trunk_type: Type[TrunkT]
    ) -> TrunkEntityRepository[TrunkT]:
        """Get a trunk repository by type."""
        if trunk_type == VacationCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._vacation_collection_repository
            )
        elif trunk_type == ProjectCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._project_collection_repository
            )
        elif trunk_type == InboxTaskCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._inbox_task_collection_repository
            )
        elif trunk_type == HabitCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._habit_collection_repository
            )
        elif trunk_type == ChoreCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._chore_collection_repository
            )
        elif trunk_type == BigPlanCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._big_plan_collection_repository
            )
        elif trunk_type == MetricCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._metric_collection_repository
            )
        elif trunk_type == SmartListCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._smart_list_collection_repository
            )
        elif trunk_type == PersonCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._person_collection_repository
            )
        elif trunk_type == PushIntegrationGroup:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._push_integration_group_repository
            )
        elif trunk_type == SlackTaskCollection:
            return typing.cast(
                TrunkEntityRepository[TrunkT], self._slack_task_collection_repository
            )
        else:
            raise Exception(f"Unknown trunk repository type {trunk_type}")

    def get_branch_repository_for(
        self, branch_type: Type[BranchT]
    ) -> BranchEntityRepository[BranchEntityKeyT, BranchT]:
        """Get a branch repository by type."""
        if branch_type == Metric:
            return typing.cast(
                BranchEntityRepository[BranchEntityKeyT, BranchT],
                self._metric_repository,
            )
        elif branch_type == SmartList:
            return typing.cast(
                BranchEntityRepository[BranchEntityKeyT, BranchT],
                self._smart_list_repository,
            )
        else:
            raise Exception(f"Unknown branch repository type {branch_type}")

    def get_leaf_repository_for(
        self, leaf_type: Type[LeafT]
    ) -> LeafEntityRepository[LeafT]:
        """Get a leaf repository by type."""
        if leaf_type == Vacation:
            return typing.cast(LeafEntityRepository[LeafT], self._vacation_repository)
        elif leaf_type == Project:
            return typing.cast(LeafEntityRepository[LeafT], self._project_repository)
        elif leaf_type == InboxTask:
            return typing.cast(LeafEntityRepository[LeafT], self._inbox_task_repository)
        elif leaf_type == Habit:
            return typing.cast(LeafEntityRepository[LeafT], self._habit_repository)
        elif leaf_type == Chore:
            return typing.cast(LeafEntityRepository[LeafT], self._chore_repository)
        elif leaf_type == BigPlan:
            return typing.cast(LeafEntityRepository[LeafT], self._big_plan_repository)
        elif leaf_type == MetricEntry:
            return typing.cast(
                LeafEntityRepository[LeafT], self._metric_entry_repository
            )
        elif leaf_type == SmartListItem:
            return typing.cast(
                LeafEntityRepository[LeafT], self._smart_list_item_repository
            )
        elif leaf_type == SmartListTag:
            return typing.cast(
                LeafEntityRepository[LeafT], self._smart_list_tag_reposiotry
            )
        elif leaf_type == Person:
            return typing.cast(LeafEntityRepository[LeafT], self._person_repository)
        elif leaf_type == SlackTask:
            return typing.cast(LeafEntityRepository[LeafT], self._slack_task_repository)
        else:
            raise Exception(f"Unknown leaf repository type {leaf_type}")


class SqliteDomainStorageEngine(DomainStorageEngine):
    """An Sqlite specific engine."""

    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, connection: SqliteConnection) -> None:
        """Constructor."""
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @contextmanager
    def get_unit_of_work(self) -> Iterator[DomainUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            workspace_repository = SqliteWorkspaceRepository(connection, self._metadata)
            vacation_collection_repository = SqliteVacationCollectionRepository(
                connection, self._metadata
            )
            vacation_repository = SqliteVacationRepository(connection, self._metadata)
            project_collection_repository = SqliteProjectCollectionRepository(
                connection, self._metadata
            )
            project_repository = SqliteProjectRepository(connection, self._metadata)
            inbox_task_collection_repository = SqliteInboxTaskCollectionRepository(
                connection, self._metadata
            )
            inbox_task_repository = SqliteInboxTaskRepository(
                connection, self._metadata
            )
            habit_collection_repository = SqliteHabitCollectionRepository(
                connection, self._metadata
            )
            habit_repository = SqliteHabitRepository(connection, self._metadata)
            chore_collection_repository = SqliteChoreCollectionRepository(
                connection, self._metadata
            )
            chore_repository = SqliteChoreRepository(connection, self._metadata)
            big_plan_collection_repository = SqliteBigPlanCollectionRepository(
                connection, self._metadata
            )
            big_plan_repository = SqliteBigPlanRepository(connection, self._metadata)
            smart_list_collection_repository = SqliteSmartListCollectionRepository(
                connection, self._metadata
            )
            smart_list_repository = SqliteSmartListRepository(
                connection, self._metadata
            )
            smart_list_tag_repository = SqliteSmartListTagRepository(
                connection, self._metadata
            )
            smart_list_item_repository = SqliteSmartListItemRepository(
                connection, self._metadata
            )
            metric_collection_repository = SqliteMetricCollectionRepository(
                connection, self._metadata
            )
            metric_repository = SqliteMetricRepository(connection, self._metadata)
            metric_entry_repository = SqliteMetricEntryRepository(
                connection, self._metadata
            )
            person_collection_repository = SqlitePersonCollectionRepository(
                connection, self._metadata
            )
            person_repository = SqlitePersonRepository(connection, self._metadata)
            push_integration_group_repository = SqlitePushIntegrationGroupRepository(
                connection, self._metadata
            )
            slack_task_collection_repository = SqliteSlackTaskCollectionRepository(
                connection, self._metadata
            )
            slack_task_repository = SqliteSlackTaskRepository(
                connection, self._metadata
            )
            notion_connection_repository = SqliteNotionConnectionRepository(
                connection, self._metadata
            )

            yield SqliteDomainUnitOfWork(
                workspace_repository=workspace_repository,
                vacation_collection_repository=vacation_collection_repository,
                vacation_repository=vacation_repository,
                project_collection_repository=project_collection_repository,
                project_repository=project_repository,
                inbox_task_collection_repository=inbox_task_collection_repository,
                inbox_task_repository=inbox_task_repository,
                habit_collection_repository=habit_collection_repository,
                habit_repository=habit_repository,
                chore_collection_repository=chore_collection_repository,
                chore_repository=chore_repository,
                big_plan_collection_repository=big_plan_collection_repository,
                big_plan_repository=big_plan_repository,
                smart_list_collection_repository=smart_list_collection_repository,
                smart_list_repository=smart_list_repository,
                smart_list_tag_repository=smart_list_tag_repository,
                smart_list_item_repository=smart_list_item_repository,
                metric_collection_repository=metric_collection_repository,
                metric_repository=metric_repository,
                metric_entry_repository=metric_entry_repository,
                person_collection_repository=person_collection_repository,
                person_repository=person_repository,
                push_integration_group_repository=push_integration_group_repository,
                slack_task_collection_repository=slack_task_collection_repository,
                slack_task_repository=slack_task_repository,
                notion_connection_repository=notion_connection_repository,
            )
