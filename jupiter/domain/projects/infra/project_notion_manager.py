"""A manager of Notion-side projects."""
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.notion_manager import NotionLeafEntityNotFoundError, ParentTrunkLeafNotionManager


class NotionProjectNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion project was not found."""


class ProjectNotionManager(
        ParentTrunkLeafNotionManager[NotionWorkspace, NotionProjectCollection, NotionProject, None]):
    """A manager of Notion-side projects."""
