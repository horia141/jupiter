"""Update the email tasks generation project."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class EmailTaskChangeGenerationProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    generation_project_ref_id: Optional[EntityId] = None


class EmailTaskChangeGenerationProjectUseCase(
    AppLoggedInMutationUseCase[EmailTaskChangeGenerationProjectArgs, None],
):
    """The command for updating the generation up project for email tasks."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return (Feature.EMAIL_TASKS, Feature.PROJECTS)

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskChangeGenerationProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            push_integration_group = (
                await uow.push_integration_group_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            email_task_collection = (
                await uow.email_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )
            old_generation_project_ref_id = (
                email_task_collection.generation_project_ref_id
            )

            if args.generation_project_ref_id is not None:
                generation_project = await uow.project_repository.load_by_id(
                    args.generation_project_ref_id,
                )
                generation_project_ref_id = generation_project.ref_id
            else:
                generation_project = await uow.project_repository.load_by_id(
                    workspace.default_project_ref_id,
                )
                generation_project_ref_id = workspace.default_project_ref_id

            email_tasks = await uow.email_task_repository.find_all(
                parent_ref_id=email_task_collection.ref_id,
                allow_archived=False,
            )
            email_tasks_by_ref_id = {st.ref_id: st for st in email_tasks}

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_generated_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.EMAIL_TASK],
                    filter_email_task_ref_ids=[m.ref_id for m in email_tasks],
                )
            )

            if (
                old_generation_project_ref_id != generation_project_ref_id
                and len(email_tasks) > 0
            ):
                updated_generated_inbox_tasks = []

                for inbox_task in all_generated_inbox_tasks:
                    email_task = email_tasks_by_ref_id[
                        cast(EntityId, inbox_task.email_task_ref_id)
                    ]
                    update_inbox_task = inbox_task.update_link_to_email_task(
                        project_ref_id=generation_project_ref_id,
                        from_address=email_task.from_address,
                        from_name=email_task.from_name,
                        to_address=email_task.to_address,
                        subject=email_task.subject,
                        body=email_task.body,
                        generation_extra_info=email_task.generation_extra_info,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )

                    await uow.inbox_task_repository.save(
                        update_inbox_task,
                    )
                    await progress_reporter.mark_updated(inbox_task)

                    updated_generated_inbox_tasks.append(update_inbox_task)

            email_task_collection = email_task_collection.change_generation_project(
                generation_project_ref_id=generation_project_ref_id,
                source=EventSource.CLI,
                modified_time=self._time_provider.get_current_time(),
            )

            await uow.email_task_collection_repository.save(email_task_collection)
