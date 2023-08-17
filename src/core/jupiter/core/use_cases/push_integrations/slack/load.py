"""Use case for loading a particular slack task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
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
class SlackTaskLoadArgs(UseCaseArgsBase):
    """SlackTaskLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class SlackTaskLoadResult(UseCaseResultBase):
    """SlackTaskLoadResult."""

    slack_task: SlackTask
    inbox_task: Optional[InboxTask] = None


class SlackTaskLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SlackTaskLoadArgs, SlackTaskLoadResult]
):
    """Use case for loading a particular slack task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SLACK_TASKS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskLoadArgs,
    ) -> SlackTaskLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        slack_task = await uow.slack_task_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_sources=[InboxTaskSource.SLACK_TASK],
            filter_slack_task_ref_ids=[slack_task.ref_id],
        )
        inbox_task = inbox_tasks[0] if len(inbox_tasks) > 0 else None

        return SlackTaskLoadResult(slack_task=slack_task, inbox_task=inbox_task)
