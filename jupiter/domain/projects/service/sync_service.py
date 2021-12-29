"""The service class for syncing the Project."""
import logging
from typing import Final, Iterable, Optional

from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.framework.base.timestamp import Timestamp

LOGGER = logging.getLogger(__name__)


class ProjectSyncService:
    """The service class for syncing the Project."""

    _storage_engine: Final[StorageEngine]
    _project_notion_manager: Final[ProjectNotionManager]

    def __init__(self, storage_engine: StorageEngine, project_notion_manager: ProjectNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._project_notion_manager = project_notion_manager

    def sync(
            self, right_now: Timestamp, filter_project_keys: Optional[Iterable[ProjectKey]],
            sync_prefer: SyncPrefer) -> Iterable[Project]:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            projects = uow.project_repository.find_all(filter_keys=filter_project_keys)

        for project in projects:
            notion_project = self._project_notion_manager.load_project(project.ref_id)

            if sync_prefer == SyncPrefer.NOTION:
                updated_project = notion_project.apply_to_aggregate_root(project, right_now)

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.project_repository.save(updated_project)
                LOGGER.info("Changed project from Notion")
            elif sync_prefer == SyncPrefer.LOCAL:
                updated_notion_project = notion_project.join_with_aggregate_root(project)
                self._project_notion_manager.save_project(updated_notion_project)
                LOGGER.info("Applied changes on Notion side")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")

        return projects
