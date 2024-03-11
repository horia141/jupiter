"""The command for finding a email task."""
from typing import cast

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class EmailTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_inbox_task: bool
    filter_ref_ids: list[EntityId] | None = None


@use_case_result_part
class EmailTaskFindResultEntry(UseCaseResultBase):
    """A single email task result."""

    email_task: EmailTask
    inbox_task: InboxTask | None = None


@use_case_result
class EmailTaskFindResult(UseCaseResultBase):
    """PersonFindResult."""

    generation_project: Project
    entries: list[EmailTaskFindResultEntry]


@readonly_use_case(WorkspaceFeature.EMAIL_TASKS)
class EmailTaskFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[EmailTaskFindArgs, EmailTaskFindResult]
):
    """The command for finding a email task."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: EmailTaskFindArgs,
    ) -> EmailTaskFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        push_integration_group = await uow.get_for(PushIntegrationGroup).load_by_parent(
            workspace.ref_id,
        )
        email_task_collection = await uow.get_for(EmailTaskCollection).load_by_parent(
            push_integration_group.ref_id,
        )
        email_tasks = await uow.get_for(EmailTask).find_all(
            parent_ref_id=email_task_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        generation_project = await uow.get_for(Project).load_by_id(
            email_task_collection.generation_project_ref_id,
        )

        if args.include_inbox_task:
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.EMAIL_TASK],
                email_task_ref_id=[st.ref_id for st in email_tasks],
            )
            inbox_tasks_by_email_task_ref_id = {
                cast(EntityId, it.email_task_ref_id): it for it in inbox_tasks
            }
        else:
            inbox_tasks_by_email_task_ref_id = None

        return EmailTaskFindResult(
            generation_project=generation_project,
            entries=[
                EmailTaskFindResultEntry(
                    email_task=st,
                    inbox_task=inbox_tasks_by_email_task_ref_id.get(st.ref_id, None)
                    if inbox_tasks_by_email_task_ref_id
                    else None,
                )
                for st in email_tasks
            ],
        )
