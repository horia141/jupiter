"""The service class for syncing the Project."""
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class ProjectSyncServiceNew(
    TrunkLeafNotionSyncService[
        ProjectCollection,
        Project,
        NotionWorkspace,
        NotionProjectCollection,
        NotionProject,
        None,
        None,
        None,
    ]
):
    """The service class for syncing the projects database between local and Notion."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        project_notion_manager: ProjectNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            ProjectCollection,
            Project,
            NotionProject,
            storage_engine,
            project_notion_manager,
        )
