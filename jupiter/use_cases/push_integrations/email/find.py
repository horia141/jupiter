"""The command for finding a email task."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class EmailTaskFindUseCase(
    AppReadonlyUseCase["EmailTaskFindUseCase.Args", "EmailTaskFindUseCase.Result"]
):
    """The command for finding a email task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        allow_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]

    @dataclass(frozen=True)
    class ResultEntry:
        """A single email task result."""

        email_task: EmailTask
        inbox_task: Optional[InboxTask]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result."""

        email_tasks: Iterable["EmailTaskFindUseCase.ResultEntry"]

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> "Result":
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            push_integration_group = (
                uow.push_integration_group_repository.load_by_parent(workspace.ref_id)
            )
            email_task_collection = uow.email_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )
            email_tasks = uow.email_task_repository.find_all(
                parent_ref_id=email_task_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
            )

            inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.EMAIL_TASK],
                filter_email_task_ref_ids=(st.ref_id for st in email_tasks),
            )
            inbox_tasks_by_email_task_ref_id = {
                cast(EntityId, it.email_task_ref_id): it for it in inbox_tasks
            }

        return EmailTaskFindUseCase.Result(
            email_tasks=[
                EmailTaskFindUseCase.ResultEntry(
                    email_task=st,
                    inbox_task=inbox_tasks_by_email_task_ref_id.get(st.ref_id, None),
                )
                for st in email_tasks
            ]
        )
