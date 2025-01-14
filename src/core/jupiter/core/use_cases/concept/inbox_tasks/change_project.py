"""The command for changing the project for an inbox task ."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    CannotModifyGeneratedTaskError,
    InboxTask,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
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
class InboxTaskChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.INBOX_TASKS, WorkspaceFeature.PROJECTS])
class InboxTaskChangeProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskChangeProjectArgs, None],
):
    """The command for changing the project of a inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.get_for(InboxTask).load_by_id(args.ref_id)

        await uow.get_for(Project).load_by_id(args.project_ref_id)

        try:
            inbox_task = inbox_task.change_project(
                ctx=context.domain_context, project_ref_id=args.project_ref_id
            )
        except CannotModifyGeneratedTaskError as err:
            raise InputValidationError(
                f"Modifying a generated task's field {err.field} is not possible",
            ) from err

        await uow.get_for(InboxTask).save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)
