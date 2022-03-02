"""The service class for syncing the Project."""

import logging
from typing import Final, Iterable, Optional, Dict

from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager, NotionProjectNotFoundError
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class ProjectSyncService:
    """The service class for syncing the Project."""

    _storage_engine: Final[DomainStorageEngine]
    _project_notion_manager: Final[ProjectNotionManager]

    def __init__(self, storage_engine: DomainStorageEngine, project_notion_manager: ProjectNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._project_notion_manager = project_notion_manager

    def sync(
            self,
            workspace: Workspace,
            filter_project_keys: Optional[Iterable[ProjectKey]],
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            sync_prefer: SyncPrefer) -> Iterable[Project]:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)
            all_projects = \
                uow.project_repository.find_all(
                    project_collection_ref_id=project_collection.ref_id,
                    allow_archived=True, filter_keys=filter_project_keys)
        all_projects_set: Dict[EntityId, Project] = {v.ref_id: v for v in all_projects}
        filter_ref_ids_set = frozenset(p.ref_id for p in all_projects) if filter_project_keys else None

        if not drop_all_notion_side:
            all_notion_projects = self._project_notion_manager.load_all_projects(project_collection.ref_id)
            all_notion_projects_notion_ids = \
                set(self._project_notion_manager.load_all_saved_project_notion_ids(project_collection.ref_id))
        else:
            self._project_notion_manager.drop_all_projects(project_collection.ref_id)
            all_notion_projects = []
            all_notion_projects_notion_ids = set()
        all_notion_projects_set: Dict[EntityId, NotionProject] = {}

        # Explore Notion and apply to local
        for notion_project in all_notion_projects:
            if filter_ref_ids_set is not None and notion_project.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_project.name}' (id={notion_project.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_project.name}' (id={notion_project.notion_id})")

            if notion_project.ref_id is None:
                new_project = \
                    notion_project.new_entity(
                        NotionProject.InverseInfo(project_collection_ref_id=project_collection.ref_id))

                with self._storage_engine.get_unit_of_work() as uow:
                    new_project = uow.project_repository.create(new_project)

                self._project_notion_manager.link_local_and_notion_entries(
                    project_collection.ref_id, new_project.ref_id, notion_project.notion_id)
                LOGGER.info("Linked the new project with local entries")

                notion_project = notion_project.join_with_entity(new_project, NotionProject.DirectInfo())
                self._project_notion_manager.save_project(project_collection.ref_id, notion_project)
                LOGGER.info(f"Applies changes on Notion side too as {notion_project}")

                all_projects_set[new_project.ref_id] = new_project
                all_notion_projects_set[new_project.ref_id] = notion_project
            elif notion_project.ref_id in all_projects_set \
                    and notion_project.notion_id in all_notion_projects_notion_ids:
                project = all_projects_set[notion_project.ref_id]
                all_notion_projects_set[notion_project.ref_id] = notion_project

                # If the project exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_project.last_edited_time <= project.last_modified_time:
                        LOGGER.info(f"Skipping {notion_project.name} because it was not modified")
                        continue

                    updated_project = \
                        notion_project.apply_to_entity(
                            project, NotionProject.InverseInfo(project_collection_ref_id=project_collection.ref_id))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.project_repository.save(updated_project)

                    all_projects_set[notion_project.ref_id] = updated_project

                    LOGGER.info(f"Changed project with id={notion_project.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified \
                            and project.last_modified_time <= notion_project.last_edited_time:
                        LOGGER.info(f"Skipping {notion_project.name} because it was not modified")
                        continue

                    updated_notion_project = \
                        notion_project.join_with_entity(project, NotionProject.DirectInfo())

                    self._project_notion_manager.save_project(project_collection.ref_id, updated_notion_project)

                    all_notion_projects_set[notion_project.ref_id] = updated_notion_project

                    LOGGER.info(f"Changed project with id={notion_project.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random project added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a project added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._project_notion_manager.remove_project(project_collection.ref_id, notion_project.ref_id)
                    LOGGER.info(f"Removed project with id={notion_project.ref_id} from Notion")
                except NotionProjectNotFoundError:
                    LOGGER.info(f"Skipped dangling project in Notion {notion_project.ref_id}")

        # Explore local and apply to Notion now
        for project in all_projects:
            if project.ref_id in all_notion_projects_set:
                # The project already exists on Notion side, so it was handled by the above loop!
                continue
            if project.archived:
                continue

            # If the project does not exist on Notion side, we create it.
            notion_project = NotionProject.new_notion_row(project, NotionProject.DirectInfo())
            self._project_notion_manager.upsert_project(project_collection.ref_id, notion_project)
            all_notion_projects_set[project.ref_id] = notion_project
            LOGGER.info(f"Created new project on Notion side {project.name}")

        return all_projects_set.values()
