"""Top level context for the application."""
from dataclasses import dataclass
from jupiter.core.domain.projects.project_name import ProjectName

from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName


@dataclass
class TopLevelContext:
    """Top level context for the application."""

    default_workspace_name: WorkspaceName
    default_first_project_name: ProjectName
    user: User | None
    workspace: Workspace | None

    def to_logged_in(self) -> "LoggedInTopLevelContext":
        """Build a logged in version of this one."""
        if self.user is None or self.workspace is None:
            raise Exception("Expected top level context to have a user and workspace")
        return LoggedInTopLevelContext(
            default_workspace_name=self.default_workspace_name,
            default_first_project_name=self.default_first_project_name,
            user=self.user, 
            workspace=self.workspace)


@dataclass
class LoggedInTopLevelContext:
    """Top level context when the user is logged in."""

    default_workspace_name: WorkspaceName
    default_first_project_name: ProjectName
    user: User
    workspace: Workspace
