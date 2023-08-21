"""Update the slack tasks generation project."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SlackTaskChangeGenerationProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    generation_project_ref_id: Optional[EntityId] = None


class SlackTaskChangeGenerationProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[SlackTaskChangeGenerationProjectArgs, None],
):
    """The command for updating the generation up project for slack tasks."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return (WorkspaceFeature.SLACK_TASKS, WorkspaceFeature.PROJECTS)

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskChangeGenerationProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        push_integration_group = (
            await uow.push_integration_group_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        slack_task_collection = (
            await uow.slack_task_collection_repository.load_by_parent(
                push_integration_group.ref_id,
            )
        )
        old_generation_project_ref_id = slack_task_collection.generation_project_ref_id

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

        slack_tasks = await uow.slack_task_repository.find_all(
            parent_ref_id=slack_task_collection.ref_id,
            allow_archived=False,
        )
        slack_tasks_by_ref_id = {st.ref_id: st for st in slack_tasks}

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        all_generated_inbox_tasks = (
            await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.SLACK_TASK],
                filter_slack_task_ref_ids=[m.ref_id for m in slack_tasks],
            )
        )

        if (
            old_generation_project_ref_id != generation_project_ref_id
            and len(slack_tasks) > 0
        ):
            updated_generated_inbox_tasks = []

            for inbox_task in all_generated_inbox_tasks:
                slack_task = slack_tasks_by_ref_id[
                    cast(EntityId, inbox_task.slack_task_ref_id)
                ]
                update_inbox_task = inbox_task.update_link_to_slack_task(
                    project_ref_id=generation_project_ref_id,
                    user=slack_task.user,
                    channel=slack_task.channel,
                    message=slack_task.message,
                    generation_extra_info=slack_task.generation_extra_info,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                await uow.inbox_task_repository.save(
                    update_inbox_task,
                )
                await progress_reporter.mark_updated(update_inbox_task)

                updated_generated_inbox_tasks.append(update_inbox_task)

        slack_task_collection = slack_task_collection.change_generation_project(
            generation_project_ref_id=generation_project_ref_id,
            source=EventSource.CLI,
            modified_time=self._time_provider.get_current_time(),
        )

        await uow.slack_task_collection_repository.save(slack_task_collection)
