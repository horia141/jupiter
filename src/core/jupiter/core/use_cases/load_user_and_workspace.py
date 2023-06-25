"""The command for loading workspaces if they exist."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.user.infra.user_repository import UserNotFoundError
from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
)
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestReadonlyUseCase,
    AppGuestUseCaseContext,
)


@dataclass
class LoadUserAndWorkspaceArgs(UseCaseArgsBase):
    """Load user and workspsace args."""


@dataclass
class LoadUserAndWorkspaceResult(UseCaseResultBase):
    """Load user and workspace result."""

    user: Optional[User] = None
    workspace: Optional[Workspace] = None


class LoadUserAndWorkspaceUseCase(
    AppGuestReadonlyUseCase[LoadUserAndWorkspaceArgs, LoadUserAndWorkspaceResult],
):
    """The command for loading a user and workspace if they exist."""

    async def _execute(
        self,
        context: AppGuestUseCaseContext,
        args: LoadUserAndWorkspaceArgs,
    ) -> LoadUserAndWorkspaceResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            if context.auth_token is None:
                user = None
                workspace = None
            else:
                try:
                    user = await uow.user_repository.load_by_id(
                        context.auth_token.user_ref_id
                    )
                    user_workspace_link = (
                        await uow.user_workspace_link_repository.load_by_user(
                            context.auth_token.user_ref_id
                        )
                    )
                    workspace = await uow.workspace_repository.load_by_id(
                        user_workspace_link.workspace_ref_id
                    )
                except (UserNotFoundError, WorkspaceNotFoundError):
                    user = None
                    workspace = None

        return LoadUserAndWorkspaceResult(user=user, workspace=workspace)
