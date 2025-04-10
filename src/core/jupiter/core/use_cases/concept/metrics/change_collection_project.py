"""Update the metrics collection project."""

from typing import cast

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.adate import ADate
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
class MetricChangeCollectionProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    collection_project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.METRICS, WorkspaceFeature.PROJECTS])
class MetricChangeCollectionProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricChangeCollectionProjectArgs, None],
):
    """The command for updating the collection up project for metrics."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricChangeCollectionProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        old_catch_up_project_ref_id = metric_collection.collection_project_ref_id

        await uow.get_for(Project).load_by_id(
            args.collection_project_ref_id,
        )

        metrics = await uow.get_for(Metric).find_all(
            parent_ref_id=metric_collection.ref_id,
            allow_archived=False,
        )

        if (
            old_catch_up_project_ref_id != args.collection_project_ref_id
            and len(metrics) > 0
        ):
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            all_collection_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.METRIC],
                source_entity_ref_id=[m.ref_id for m in metrics],
            )

            for inbox_task in all_collection_inbox_tasks:
                inbox_task = inbox_task.update_link_to_metric(
                    context.domain_context,
                    project_ref_id=args.collection_project_ref_id,
                    name=inbox_task.name,
                    recurring_timeline=cast(str, inbox_task.recurring_timeline),
                    eisen=inbox_task.eisen,
                    difficulty=inbox_task.difficulty,
                    actionable_date=inbox_task.actionable_date,
                    due_time=cast(ADate, inbox_task.due_date),
                )

                inbox_task = await uow.get_for(InboxTask).save(
                    inbox_task,
                )
                await progress_reporter.mark_updated(inbox_task)

            metric_collection = metric_collection.change_collection_project(
                context.domain_context,
                collection_project_ref_id=args.collection_project_ref_id,
            )

            await uow.get_for(MetricCollection).save(metric_collection)
