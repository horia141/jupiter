"""Use case for loading a particular email task."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class EmailTaskLoadArgs(UseCaseArgsBase):
    """EmailTaskLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class EmailTaskLoadResult(UseCaseResultBase):
    """EmailTaskLoadResult."""

    email_task: EmailTask
    inbox_task: InboxTask | None


@readonly_use_case(WorkspaceFeature.EMAIL_TASKS)
class EmailTaskLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[EmailTaskLoadArgs, EmailTaskLoadResult]
):
    """Use case for loading a particular email task."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: EmailTaskLoadArgs,
    ) -> EmailTaskLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        email_task = await uow.get_for(EmailTask).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.EMAIL_TASK,
            source_entity_ref_id=email_task.ref_id,
        )
        inbox_task = inbox_tasks[0] if len(inbox_tasks) > 0 else None

        return EmailTaskLoadResult(email_task=email_task, inbox_task=inbox_task)
