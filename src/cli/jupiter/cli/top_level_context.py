"""Top level context for the application."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName


@dataclass(frozen=True)
class TopLevelContext:
    """Top level context for the application."""

    default_workspace_name: WorkspaceName
    default_first_project_name: ProjectName
    user: User | None
    workspace: Workspace | None


@dataclass(frozen=True)
class LoggedInTopLevelContext:
    """Top level context when the user is logged in."""

    default_workspace_name: WorkspaceName
    default_first_project_name: ProjectName
    user: User
    workspace: Workspace
