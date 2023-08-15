"""The command for finding a slack task."""
from dataclasses import dataclass
from typing import Iterable, List, Optional, cast

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class SlackTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_inbox_tasks: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@dataclass
class SlackTaskFindResultEntry:
    """A single slack task result."""

    slack_task: SlackTask
    inbox_task: Optional[InboxTask] = None


@dataclass
class SlackTaskFindResult(UseCaseResultBase):
    """PersonFindResult."""

    generation_project: Project
    entries: List[SlackTaskFindResultEntry]


class SlackTaskFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SlackTaskFindArgs, SlackTaskFindResult]
):
    """The command for finding a slack task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SLACK_TASKS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskFindArgs,
    ) -> SlackTaskFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
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

        slack_tasks = await uow.slack_task_repository.find_all(
            parent_ref_id=slack_task_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        generation_project = await uow.project_repository.load_by_id(
            slack_task_collection.generation_project_ref_id,
        )

        if args.include_inbox_tasks:
            inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.SLACK_TASK],
                filter_slack_task_ref_ids=(st.ref_id for st in slack_tasks),
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
