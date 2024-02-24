"""The command for updating a email task."""
from typing import Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
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
class EmailTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    from_address: UpdateAction[EmailAddress]
    from_name: UpdateAction[EmailUserName]
    to_address: UpdateAction[EmailAddress]
    subject: UpdateAction[str]
    body: UpdateAction[str]
    generation_name: UpdateAction[Optional[InboxTaskName]]
    generation_status: UpdateAction[Optional[InboxTaskStatus]]
    generation_eisen: UpdateAction[Optional[Eisen]]
    generation_difficulty: UpdateAction[Optional[Difficulty]]
    generation_actionable_date: UpdateAction[Optional[ADate]]
    generation_due_date: UpdateAction[Optional[ADate]]


@mutation_use_case(WorkspaceFeature.EMAIL_TASKS)
class EmailTaskUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[EmailTaskUpdateArgs, None]
):
    """The command for updating a email task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: EmailTaskUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        email_task = await uow.repository_for(EmailTask).load_by_id(args.ref_id)

        if (
            args.generation_name.should_change
            or args.generation_status.should_change
            or args.generation_eisen.should_change
            or args.generation_difficulty.should_change
            or args.generation_actionable_date.should_change
            or args.generation_due_date.should_change
        ):
            generation_extra_info = UpdateAction.change_to(
                PushGenerationExtraInfo(
                    timezone=user.timezone,
                    name=args.generation_name.or_else(
                        email_task.generation_extra_info.name,
                    ),
                    status=args.generation_status.or_else(
                        email_task.generation_extra_info.status,
                    ),
                    eisen=args.generation_eisen.or_else(
                        email_task.generation_extra_info.eisen,
                    ),
                    difficulty=args.generation_difficulty.or_else(
                        email_task.generation_extra_info.difficulty,
                    ),
                    actionable_date=args.generation_actionable_date.or_else(
                        email_task.generation_extra_info.actionable_date,
                    ),
                    due_date=args.generation_due_date.or_else(
                        email_task.generation_extra_info.due_date,
                    ),
                ),
            )
        else:
            generation_extra_info = UpdateAction.do_nothing()

        inbox_task_collection = await uow.repository_for(
            InboxTaskCollection
        ).load_by_parent(
            workspace.ref_id,
        )
        generated_inbox_task = (
            await uow.repository_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                source=[InboxTaskSource.EMAIL_TASK],
                email_task_ref_id=[email_task.ref_id],
            )
        )[0]

        generated_inbox_task = generated_inbox_task.update_link_to_email_task(
            ctx=context.domain_context,
            project_ref_id=generated_inbox_task.project_ref_id,
            from_address=email_task.from_address,
            from_name=email_task.from_name,
            to_address=email_task.to_address,
            subject=email_task.subject,
            body=email_task.body,
            generation_extra_info=email_task.generation_extra_info,
        )

        await uow.repository_for(InboxTask).save(generated_inbox_task)
        await progress_reporter.mark_updated(generated_inbox_task)

        email_task = email_task.update(
            ctx=context.domain_context,
            from_address=args.from_address,
            from_name=args.from_name,
            to_address=args.to_address,
            subject=args.subject,
            body=args.body,
            generation_extra_info=generation_extra_info,
        )

        await uow.repository_for(EmailTask).save(email_task)
        await progress_reporter.mark_updated(email_task)
