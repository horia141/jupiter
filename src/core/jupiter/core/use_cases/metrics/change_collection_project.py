"""Update the metrics collection project."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain.adate import ADate
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
class MetricChangeCollectionProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    collection_project_ref_id: Optional[EntityId] = None


class MetricChangeCollectionProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricChangeCollectionProjectArgs, None],
):
    """The command for updating the collection up project for metrics."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return (WorkspaceFeature.METRICS, WorkspaceFeature.PROJECTS)

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricChangeCollectionProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        await uow.project_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        metric_collection = await uow.metric_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        old_catch_up_project_ref_id = metric_collection.collection_project_ref_id

        if args.collection_project_ref_id is not None:
            project = await uow.project_repository.load_by_id(
                args.collection_project_ref_id,
            )
            collection_project_ref_id = project.ref_id
        else:
            collection_project_ref_id = workspace.default_project_ref_id

        metrics = await uow.metric_repository.find_all(
            parent_ref_id=metric_collection.ref_id,
            allow_archived=False,
        )

        if (
            old_catch_up_project_ref_id != collection_project_ref_id
            and len(metrics) > 0
        ):
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_collection_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.METRIC],
                    filter_metric_ref_ids=[m.ref_id for m in metrics],
                )
            )

            for inbox_task in all_collection_inbox_tasks:
                inbox_task = inbox_task.update_link_to_metric(
                    project_ref_id=collection_project_ref_id,
                    name=inbox_task.name,
                    recurring_timeline=cast(str, inbox_task.recurring_timeline),
                    eisen=inbox_task.eisen,
                    difficulty=inbox_task.difficulty,
                    actionable_date=inbox_task.actionable_date,
                    due_time=cast(ADate, inbox_task.due_date),
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                inbox_task = await uow.inbox_task_repository.save(
                    inbox_task,
                )
                await progress_reporter.mark_updated(inbox_task)

            metric_collection = metric_collection.change_collection_project(
                collection_project_ref_id=collection_project_ref_id,
                source=EventSource.CLI,
                modified_time=self._time_provider.get_current_time(),
            )

            await uow.metric_collection_repository.save(metric_collection)
