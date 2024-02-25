"""The command for finding a slack task."""
from typing import List, Optional, cast

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
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
class SlackTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_inbox_tasks: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@use_case_result_part
class SlackTaskFindResultEntry(UseCaseResultBase):
    """A single slack task result."""

    slack_task: SlackTask
    inbox_task: Optional[InboxTask] = None


@use_case_result
class SlackTaskFindResult(UseCaseResultBase):
    """PersonFindResult."""

    generation_project: Project
    entries: List[SlackTaskFindResultEntry]


@readonly_use_case(WorkspaceFeature.SLACK_TASKS)
class SlackTaskFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SlackTaskFindArgs, SlackTaskFindResult]
):
    """The command for finding a slack task."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SlackTaskFindArgs,
    ) -> SlackTaskFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        push_integration_group = await uow.get_for(PushIntegrationGroup).load_by_parent(
            workspace.ref_id,
        )
        slack_task_collection = await uow.get_for(SlackTaskCollection).load_by_parent(
            push_integration_group.ref_id,
        )

        slack_tasks = await uow.get_for(SlackTask).find_all(
            parent_ref_id=slack_task_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        generation_project = await uow.get_for(Project).load_by_id(
            slack_task_collection.generation_project_ref_id,
        )

        if args.include_inbox_tasks:
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.SLACK_TASK],
                slack_task_ref_id=[st.ref_id for st in slack_tasks],
            )
            inbox_tasks_by_slack_task_ref_id = {
                cast(EntityId, it.slack_task_ref_id): it for it in inbox_tasks
            }
        else:
            inbox_tasks_by_slack_task_ref_id = None

        return SlackTaskFindResult(
            generation_project=generation_project,
            entries=[
                SlackTaskFindResultEntry(
                    slack_task=st,
                    inbox_task=inbox_tasks_by_slack_task_ref_id.get(st.ref_id, None)
                    if inbox_tasks_by_slack_task_ref_id
                    else None,
                )
                for st in slack_tasks
            ],
        )
