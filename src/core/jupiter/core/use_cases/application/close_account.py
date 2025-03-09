"""Close an account and workspace."""
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.infra.generic_full_archiver import generic_full_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class CloseAccountArgs(UseCaseArgsBase):
    """Close account args."""


@secure_class
class CloseAccountUseCase(
    AppTransactionalLoggedInMutationUseCase[CloseAccountArgs, None]
):
    """Close account use case."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CloseAccountArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            user_workspace_link = await uow.get(
                UserWorkspaceLinkRepository
            ).load_by_user(user.ref_id)
            await generic_full_archiver(
                context.domain_context,
                uow,
                UserWorkspaceLink,
                user_workspace_link.ref_id,
            )

            await generic_full_archiver(
                context.domain_context, uow, Workspace, workspace.ref_id
            )
            await generic_full_archiver(context.domain_context, uow, User, user.ref_id)
