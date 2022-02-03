"""The real implementation of an engine."""
import json
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, Iterator, Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine
from sqlalchemy.future import Engine

from jupiter.domain.big_plans.infra.big_plan_collection_repository import BigPlanCollectionRepository
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.domain.inbox_tasks.infra.inbox_task_collection_repository import InboxTaskCollectionRepository
from jupiter.domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository
from jupiter.domain.metrics.infra.metric_collection_repository import MetricCollectionRepository
from jupiter.domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from jupiter.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.domain.persons.infra.person_repository import PersonRepository
from jupiter.domain.persons.infra.person_collection_repository import PersonCollectionRepository
from jupiter.domain.projects.infra.project_collection_repository import ProjectCollectionRepository
from jupiter.domain.projects.infra.project_repository import ProjectRepository
from jupiter.domain.recurring_tasks.infra.recurring_task_collection_repository import RecurringTaskCollectionRepository
from jupiter.domain.recurring_tasks.infra.recurring_task_repository import RecurringTaskRepository
from jupiter.domain.remote.notion.collection_repository import NotionConnectionRepository
from jupiter.domain.smart_lists.infra.smart_list_collection_repository import SmartListCollectionRepository
from jupiter.domain.smart_lists.infra.smart_list_item_repository import SmartListItemRepository
from jupiter.domain.smart_lists.infra.smart_list_repository import SmartListRepository
from jupiter.domain.smart_lists.infra.smart_list_tag_repository import SmartListTagRepository
from jupiter.domain.storage_engine import DomainUnitOfWork, DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_collection_repository import VacationCollectionRepository
from jupiter.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository
from jupiter.repository.sqlite.domain.big_plans import SqliteBigPlanCollectionRepository, SqliteBigPlanRepository
from jupiter.repository.sqlite.domain.inbox_tasks import SqliteInboxTaskCollectionRepository, SqliteInboxTaskRepository
from jupiter.repository.sqlite.domain.metrics import SqliteMetricRepository, SqliteMetricEntryRepository, \
    SqliteMetricCollectionRepository
from jupiter.repository.sqlite.domain.persons import SqlitePersonCollectionRepository, SqlitePersonRepository
from jupiter.repository.sqlite.domain.projects import SqliteProjectRepository, SqliteProjectCollectionRepository
from jupiter.repository.sqlite.domain.recurring_tasks import SqliteRecurringTaskCollectionRepository, \
    SqliteRecurringTaskRepository
from jupiter.repository.sqlite.domain.remote.notion.connections import SqliteNotionConnectionRepository
from jupiter.repository.sqlite.domain.smart_lists import SqliteSmartListRepository, SqliteSmartListTagRepository, \
    SqliteSmartListItemRepository, SqliteSmartListCollectionRepository
from jupiter.repository.sqlite.domain.vacations import SqliteVacationRepository, SqliteVacationCollectionRepository
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
    _recurring_task_collection_repository: Final[SqliteRecurringTaskCollectionRepository]
    _recurring_task_repository: Final[SqliteRecurringTaskRepository]
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
            recurring_task_collection_repository: SqliteRecurringTaskCollectionRepository,
            recurring_task_repository: SqliteRecurringTaskRepository,
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
            notion_connection_repository: SqliteNotionConnectionRepository) -> None:
        """Constructor."""
        self._workspace_repository = workspace_repository
        self._vacation_collection_repository = vacation_collection_repository
        self._vacation_repository = vacation_repository
        self._project_collection_repository = project_collection_repository
        self._project_repository = project_repository
        self._inbox_task_collection_repository = inbox_task_collection_repository
        self._inbox_task_repository = inbox_task_repository
        self._recurring_task_collection_repository = recurring_task_collection_repository
        self._recurring_task_repository = recurring_task_repository
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
        self._notion_connection_repository = notion_connection_repository

    def __enter__(self) -> 'SqliteDomainUnitOfWork':
        """Enter the context."""
        return self

    def __exit__(
            self, _exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
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
    def recurring_task_collection_repository(self) -> RecurringTaskCollectionRepository:
        """The recurring task collection repository."""
        return self._recurring_task_collection_repository

    @property
    def recurring_task_repository(self) -> RecurringTaskRepository:
        """The recurring task repository."""
        return self._recurring_task_repository

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
    def notion_connection_repository(self) -> NotionConnectionRepository:
        """The Notion connection repository."""
        return self._notion_connection_repository


class SqliteDomainStorageEngine(DomainStorageEngine):
    """An Sqlite specific engine."""

    @dataclass(frozen=True)
    class Config:
        """Config for a Sqlite metric engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _config: Final[Config]
    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, config: Config) -> None:
        """Constructor."""
        self._config = config
        self._sql_engine = create_engine(config.sqlite_db_url, future=True, json_serializer=json.dumps)
        self._metadata = MetaData(bind=self._sql_engine)

    def prepare(self) -> None:
        """Prepare the environment for SQLite."""
        with self._sql_engine.begin() as connection:
            alembic_cfg = Config(str(self._config.alembic_ini_path))
            alembic_cfg.set_section_option('alembic', 'script_location', str(self._config.alembic_migrations_path))
            # pylint: disable=unsupported-assignment-operation
            alembic_cfg.attributes['connection'] = connection
            command.upgrade(alembic_cfg, 'head')

    @contextmanager
    def get_unit_of_work(self) -> Iterator[DomainUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            workspace_repository = SqliteWorkspaceRepository(connection, self._metadata)
            vacation_collection_repository = SqliteVacationCollectionRepository(connection, self._metadata)
            vacation_repository = SqliteVacationRepository(connection, self._metadata)
            project_collection_repository = SqliteProjectCollectionRepository(connection, self._metadata)
            project_repository = SqliteProjectRepository(connection, self._metadata)
            inbox_task_collection_repository = SqliteInboxTaskCollectionRepository(connection, self._metadata)
            inbox_task_repository = SqliteInboxTaskRepository(connection, self._metadata)
            recurring_task_collection_repository = SqliteRecurringTaskCollectionRepository(connection, self._metadata)
            recurring_task_repository = SqliteRecurringTaskRepository(connection, self._metadata)
            big_plan_collection_repository = SqliteBigPlanCollectionRepository(connection, self._metadata)
            big_plan_repository = SqliteBigPlanRepository(connection, self._metadata)
            smart_list_collection_repository = SqliteSmartListCollectionRepository(connection, self._metadata)
            smart_list_repository = SqliteSmartListRepository(connection, self._metadata)
            smart_list_tag_repository = SqliteSmartListTagRepository(connection, self._metadata)
            smart_list_item_repository = SqliteSmartListItemRepository(connection, self._metadata)
            metric_collection_repository = SqliteMetricCollectionRepository(connection, self._metadata)
            metric_repository = SqliteMetricRepository(connection, self._metadata)
            metric_entry_repository = SqliteMetricEntryRepository(connection, self._metadata)
            person_collection_repository = SqlitePersonCollectionRepository(connection, self._metadata)
            person_repository = SqlitePersonRepository(connection, self._metadata)
            notion_connection_repository = SqliteNotionConnectionRepository(connection, self._metadata)

            yield SqliteDomainUnitOfWork(
                workspace_repository=workspace_repository,
                vacation_collection_repository=vacation_collection_repository,
                vacation_repository=vacation_repository,
                project_collection_repository=project_collection_repository,
                project_repository=project_repository,
                inbox_task_collection_repository=inbox_task_collection_repository,
                inbox_task_repository=inbox_task_repository,
                recurring_task_collection_repository=recurring_task_collection_repository,
                recurring_task_repository=recurring_task_repository,
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
                notion_connection_repository=notion_connection_repository)
