"""A temporary migrator."""
import logging

import coloredlogs

from repository.sqlite.metrics import SqliteMetricEngine
from repository.workspace import WorkspaceRepository, MissingWorkspaceRepositoryError
from repository.yaml.metrics import YamlMetricEngine
from utils.global_properties import build_global_properties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    workspaces_repository = WorkspaceRepository(time_provider)

    try:
        workspace = workspaces_repository.load_workspace()
        timezone = workspace.timezone
    except MissingWorkspaceRepositoryError:
        timezone = None

    global_properties = build_global_properties(timezone)
    yaml_metric_engine = YamlMetricEngine(time_provider)
    sqlite_metric_engine = SqliteMetricEngine(
        SqliteMetricEngine.Config(
            global_properties.sqlite_db_url, global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path))

    coloredlogs.install(
        level="info",
        fmt="%(asctime)s %(name)-12s %(levelname)-6s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    sqlite_metric_engine.prepare()

    with yaml_metric_engine.get_unit_of_work() as yaml_uow:
        with sqlite_metric_engine.get_unit_of_work() as sqlite_uow:
            for metric in yaml_uow.metric_repository.find_all(allow_archived=True):
                sqlite_uow.metric_repository.create(metric)

            for metric_entry in yaml_uow.metric_entry_repository.find_all(allow_archived=True):
                sqlite_uow.metric_entry_repository.create(metric_entry)



if __name__ == "__main__":
    main()
