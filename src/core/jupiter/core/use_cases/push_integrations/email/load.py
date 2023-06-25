"""Use case for loading a particular email task."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class EmailTaskLoadArgs(UseCaseArgsBase):
    """EmailTaskLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class EmailTaskLoadResult(UseCaseResultBase):
    """EmailTaskLoadResult."""

    email_task: EmailTask
    inbox_task: Optional[InboxTask] = None


class EmailTaskLoadUseCase(
    AppLoggedInReadonlyUseCase[EmailTaskLoadArgs, EmailTaskLoadResult]
):
    """Use case for loading a particular email task."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskLoadArgs,
    ) -> EmailTaskLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        async with self._storage_engine.get_unit_of_work() as uow:
            email_task = await uow.email_task_repository.load_by_id(
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
                filter_sources=[InboxTaskSource.EMAIL_TASK],
                filter_email_task_ref_ids=[email_task.ref_id],
            )
            inbox_task = inbox_tasks[0] if len(inbox_tasks) > 0 else None

        return EmailTaskLoadResult(email_task=email_task, inbox_task=inbox_task)
