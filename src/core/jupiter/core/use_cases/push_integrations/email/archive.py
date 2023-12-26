"""The command for archiving a email task."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.push_integrations.email.service.archive_service import (
    EmailTaskArchiveService,
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
class EmailTaskArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.EMAIL_TASKS)
class EmailTaskArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[EmailTaskArchiveArgs, None]
):
    """The command for archiving a email task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: EmailTaskArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        email_task = await uow.email_task_repository.load_by_id(ref_id=args.ref_id)

        email_task_archive_service = EmailTaskArchiveService()

        await email_task_archive_service.do_it(
            context.domain_context, uow, progress_reporter, email_task
        )
