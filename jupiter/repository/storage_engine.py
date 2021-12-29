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
from jupiter.domain.storage_engine import UnitOfWork, StorageEngine
from jupiter.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository
from jupiter.repository.sqlite.metrics import SqliteMetricRepository, SqliteMetricEntryRepository
from jupiter.repository.sqlite.prm import SqlitePrmDatabaseRepository, SqlitePersonRepository
from jupiter.repository.yaml.big_plans import YamlBigPlanCollectionRepository, YamlBigPlanRepository
from jupiter.repository.yaml.inbox_tasks import YamlInboxTaskCollectionRepository, YamlInboxTaskRepository
from jupiter.repository.yaml.projects import YamlProjectRepository
from jupiter.repository.yaml.recurring_tasks import YamlRecurringTaskCollectionRepository, YamlRecurringTaskRepository
from jupiter.repository.yaml.smart_lists import YamlSmartListRepository, YamlSmartListTagRepository, \
    YamlSmartListItemRepository
from jupiter.repository.yaml.vacations import YamlVacationRepository
from jupiter.repository.yaml.workspace import YamlWorkspaceRepository
from jupiter.utils.time_provider import TimeProvider


class SqliteUnitOfWork(UnitOfWork):
    """A Sqlite specific metric unit of work."""

    _workspace_repository: Final[YamlWorkspaceRepository]
    _vacation_repository: Final[YamlVacationRepository]
    _project_repository: Final[YamlProjectRepository]
    _inbox_task_collection_repository: Final[YamlInboxTaskCollectionRepository]
    _inbox_task_repository: Final[YamlInboxTaskRepository]
    _recurring_task_collection_repository: Final[YamlRecurringTaskCollectionRepository]
    _recurring_task_repository: Final[YamlRecurringTaskRepository]
    _big_plan_collection_repository: Final[YamlBigPlanCollectionRepository]
    _big_plan_repository: Final[YamlBigPlanRepository]
    _smart_list_repository: Final[YamlSmartListRepository]
    _smart_list_tag_reposiotry: Final[YamlSmartListTagRepository]
    _smart_list_item_repository: Final[YamlSmartListItemRepository]
    _metric_repository: Final[SqliteMetricRepository]
    _metric_entry_repository: Final[SqliteMetricEntryRepository]
    _prm_database_repository: Final[SqlitePrmDatabaseRepository]
    _person_repository: Final[SqlitePersonRepository]

    def __init__(
            self,
            time_provider: TimeProvider,
            metric_repository: SqliteMetricRepository,
            metric_entry_repository: SqliteMetricEntryRepository,
            prm_database_repository: SqlitePrmDatabaseRepository,
            person_repository: SqlitePersonRepository) -> None:
        """Constructor."""
        self._workspace_repository = YamlWorkspaceRepository(time_provider)
        self._vacation_repository = YamlVacationRepository(time_provider)
        self._project_repository = YamlProjectRepository(time_provider)
        self._inbox_task_collection_repository = YamlInboxTaskCollectionRepository(time_provider)
        self._inbox_task_repository = YamlInboxTaskRepository(time_provider)
        self._recurring_task_collection_repository = YamlRecurringTaskCollectionRepository(time_provider)
        self._recurring_task_repository = YamlRecurringTaskRepository(time_provider)
        self._big_plan_collection_repository = YamlBigPlanCollectionRepository(time_provider)
        self._big_plan_repository = YamlBigPlanRepository(time_provider)
        self._smart_list_repository = YamlSmartListRepository(time_provider)
        self._smart_list_tag_reposiotry = YamlSmartListTagRepository(time_provider)
        self._smart_list_item_repository = YamlSmartListItemRepository(time_provider)
        self._metric_repository = metric_repository
        self._metric_entry_repository = metric_entry_repository
        self._prm_database_repository = prm_database_repository
        self._person_repository = person_repository

    def __enter__(self) -> 'SqliteUnitOfWork':
        """Enter the context."""
        self._workspace_repository.initialize()
        self._vacation_repository.initialize()
        self._project_repository.initialize()
        self._inbox_task_collection_repository.initialize()
        self._inbox_task_repository.initialize()
        self._recurring_task_collection_repository.initialize()
        self._recurring_task_repository.initialize()
        self._big_plan_collection_repository.initialize()
        self._big_plan_repository.initialize()
        self._smart_list_repository.initialize()
        self._smart_list_tag_reposiotry.initialize()
        self._smart_list_item_repository.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""

    @property
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace repository."""
        return self._workspace_repository

    @property
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""
        return self._vacation_repository

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
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""
        return self._metric_repository

    @property
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""
        return self._metric_entry_repository

    @property
    def prm_database_repository(self) -> PrmDatabaseRepository:
        """The PRM database repository."""
        return self._prm_database_repository

    @property
    def person_repository(self) -> PersonRepository:
        """The person repository."""
        return self._person_repository


class SqliteStorageEngine(StorageEngine):
    """An Sqlite specific engine."""

    @dataclass(frozen=True)
    class Config:
        """Config for a Sqlite metric engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _time_provider: Final[TimeProvider]
    _config: Final[Config]
    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, time_provider: TimeProvider, config: Config) -> None:
        """Constructor."""
        self._time_provider = time_provider
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
    def get_unit_of_work(self) -> Iterator[UnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            metric_repository = SqliteMetricRepository(connection, self._metadata)
            metric_entry_repository = SqliteMetricEntryRepository(connection, self._metadata)
            prm_database_repository = SqlitePrmDatabaseRepository(connection, self._metadata)
            person_repository = SqlitePersonRepository(connection, self._metadata)
            yield SqliteUnitOfWork(
                self._time_provider,
                metric_repository, metric_entry_repository,
                prm_database_repository, person_repository)
