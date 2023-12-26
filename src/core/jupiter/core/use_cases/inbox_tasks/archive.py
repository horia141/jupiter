"""The command for archiving a inbox task."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class InboxTaskArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskArchiveArgs, None]
):
    """The command for archiving a inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)
        await InboxTaskArchiveService().do_it(
            context.domain_context, uow, progress_reporter, inbox_task
        )
