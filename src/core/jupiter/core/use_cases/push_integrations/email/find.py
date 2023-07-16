"""The command for finding a email task."""
from dataclasses import dataclass
from typing import Iterable, List, Optional, cast

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.projects.project import Project
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
class EmailTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_inbox_task: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@dataclass
class EmailTaskFindResultEntry:
    """A single email task result."""

    email_task: EmailTask
    inbox_task: Optional[InboxTask] = None


@dataclass
class EmailTaskFindResult(UseCaseResultBase):
    """PersonFindResult."""

    generation_project: Project
    entries: List[EmailTaskFindResultEntry]


class EmailTaskFindUseCase(
    AppLoggedInReadonlyUseCase[EmailTaskFindArgs, EmailTaskFindResult]
):
    """The command for finding a email task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.EMAIL_TASKS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskFindArgs,
    ) -> EmailTaskFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
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
            email_task_collection = (
                await uow.email_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )
            email_tasks = await uow.email_task_repository.find_all(
                parent_ref_id=email_task_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
            )

            generation_project = await uow.project_repository.load_by_id(
                email_task_collection.generation_project_ref_id,
            )

            if args.include_inbox_task:
                inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.EMAIL_TASK],
                    filter_email_task_ref_ids=(st.ref_id for st in email_tasks),
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
