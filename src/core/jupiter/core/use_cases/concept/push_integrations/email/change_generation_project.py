"""Update the email tasks generation project."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.features import WorkspaceFeature
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
class EmailTaskChangeGenerationProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    generation_project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.EMAIL_TASKS, WorkspaceFeature.PROJECTS])
class EmailTaskChangeGenerationProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[EmailTaskChangeGenerationProjectArgs, None],
):
    """The command for updating the generation up project for email tasks."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: EmailTaskChangeGenerationProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        push_integration_group = await uow.get_for(PushIntegrationGroup).load_by_parent(
            workspace.ref_id,
        )
        email_task_collection = await uow.get_for(EmailTaskCollection).load_by_parent(
            push_integration_group.ref_id,
        )
        old_generation_project_ref_id = email_task_collection.generation_project_ref_id

        await uow.get_for(Project).load_by_id(
            args.generation_project_ref_id,
        )

        email_tasks = await uow.get_for(EmailTask).find_all(
            parent_ref_id=email_task_collection.ref_id,
            allow_archived=False,
        )
        email_tasks_by_ref_id = {st.ref_id: st for st in email_tasks}

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        all_generated_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=[InboxTaskSource.EMAIL_TASK],
            source_entity_ref_id=[m.ref_id for m in email_tasks],
        )

        if (
            old_generation_project_ref_id != args.generation_project_ref_id
            and len(email_tasks) > 0
        ):
            updated_generated_inbox_tasks = []

            for inbox_task in all_generated_inbox_tasks:
                email_task = email_tasks_by_ref_id[
                    inbox_task.source_entity_ref_id_for_sure
                ]
                update_inbox_task = inbox_task.update_link_to_email_task(
                    ctx=context.domain_context,
                    project_ref_id=args.generation_project_ref_id,
                    from_address=email_task.from_address,
                    from_name=email_task.from_name,
                    to_address=email_task.to_address,
                    subject=email_task.subject,
                    body=email_task.body,
                    generation_extra_info=email_task.generation_extra_info,
                )

                await uow.get_for(InboxTask).save(
                    update_inbox_task,
                )
                await progress_reporter.mark_updated(inbox_task)

                updated_generated_inbox_tasks.append(update_inbox_task)

        email_task_collection = email_task_collection.change_generation_project(
            context.domain_context,
            generation_project_ref_id=args.generation_project_ref_id,
        )

        await uow.get_for(EmailTaskCollection).save(email_task_collection)
