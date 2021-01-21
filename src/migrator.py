"""A temporary migrator."""
import logging
import os
from pathlib import Path
from typing import cast

import coloredlogs
import dotenv
import pendulum

from models.basic import BasicValidator, EntityId
from remote.notion.big_plans_manager import NotionBigPlansManager
from remote.notion.infra.collections_manager import CollectionsManager
from remote.notion.infra.connection import NotionConnection
from repository.projects import ProjectsRepository
from repository.workspace import WorkspaceRepository, MissingWorkspaceRepositoryError
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    notion_connection = NotionConnection()

    workspaces_repository = WorkspaceRepository(time_provider)

    global_properties = _build_global_properties(workspaces_repository)
    basic_validator = BasicValidator(global_properties)

    coloredlogs.install(
        level="info",
        fmt="%(asctime)s %(name)-12s %(levelname)-6s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    with ProjectsRepository(time_provider) as projects_repository, \
        CollectionsManager(time_provider, notion_connection) as collections_manager:
        notion_big_plans_manager = NotionBigPlansManager(time_provider, basic_validator, collections_manager)

        for project_row in projects_repository.find_all_projects():
            LOGGER.info(f'Processing project "{project_row.name}"')
            all_big_plan_notion_rows = notion_big_plans_manager.load_all_big_plans(project_row.ref_id)

            for big_plan_notion_row in all_big_plan_notion_rows:
                LOGGER.info(f'Processing big plan "{big_plan_notion_row.name}"')
                if big_plan_notion_row.ref_id is None:
                    LOGGER.info(f'Empty ... skipping')
                    continue
                notion_big_plans_manager.link_local_and_notion_entries(
                    project_row.ref_id, EntityId(big_plan_notion_row.ref_id), big_plan_notion_row.notion_id)


def _build_global_properties(workspace_repository: WorkspaceRepository) -> GlobalProperties:
    config_path = Path(os.path.realpath(Path(os.path.realpath(__file__)).parent / ".." / "Config"))

    if not config_path.exists():
        raise Exception("Critical error - missing Config file")

    dotenv.load_dotenv(dotenv_path=config_path, verbose=True)

    description = cast(str, os.getenv("DESCRIPTION"))
    version = cast(str, os.getenv("VERSION"))
    docs_init_workspace_url = cast(str, os.getenv("DOCS_INIT_WORKSPACE_URL"))
    docs_update_expired_token_url = cast(str, os.getenv("DOCS_UPDATE_EXPIRED_TOKEN_URL"))
    docs_fix_data_inconsistencies_url = cast(str, os.getenv("DOCS_FIX_DATA_INCONSISTENCIES_URL"))

    try:
        workspace = workspace_repository.load_workspace()
        timezone = workspace.timezone
    except MissingWorkspaceRepositoryError:
        timezone = pendulum.timezone(os.getenv("TZ", "UTC"))

    return GlobalProperties(
        description=description,
        version=version,
        timezone=timezone,
        docs_init_workspace_url=docs_init_workspace_url,
        docs_update_expired_token_url=docs_update_expired_token_url,
        docs_fix_data_inconsistencies_url=docs_fix_data_inconsistencies_url)


if __name__ == "__main__":
    main()
