"""The command for hard removing a email task."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class EmailTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.EMAIL_TASKS)
class EmailTaskRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[EmailTaskRemoveArgs, None]
):
    """The command for archiving a email task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: EmailTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        email_task = await uow.repository_for(EmailTask).load_by_id(ref_id=args.ref_id)

        email_task_remove_service = EmailTaskRemoveService()

        await email_task_remove_service.do_it(
            context.domain_context, uow, progress_reporter, email_task
        )
