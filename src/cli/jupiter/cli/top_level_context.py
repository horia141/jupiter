"""Top level context for the application."""
from dataclasses import dataclass

from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.workspace import Workspace


@dataclass
class TopLevelContext:
    """Top level context for the application."""

    user: User | None
    workspace: Workspace | None

    def to_logged_in(self) -> "LoggedInTopLevelContext":
        """Build a logged in version of this one."""
        if self.user is None or self.workspace is None:
            raise Exception("Expected top level context to have a user and workspace")
        return LoggedInTopLevelContext(user=self.user, workspace=self.workspace)


@dataclass
class LoggedInTopLevelContext:
    """Top level context when the user is logged in."""

    user: User
    workspace: Workspace
