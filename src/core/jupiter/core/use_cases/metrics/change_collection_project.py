"""Update the metrics collection project."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricChangeCollectionProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    collection_project_ref_id: Optional[EntityId] = None


class MetricChangeCollectionProjectUseCase(
    AppLoggedInMutationUseCase[MetricChangeCollectionProjectArgs, None],
):
    """The command for updating the collection up project for metrics."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return (Feature.METRICS, Feature.PROJECTS)

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricChangeCollectionProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
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
            async with self._domain_storage_engine.get_unit_of_work() as inbox_task_uow:
                inbox_task_collection = await inbox_task_uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
                all_collection_inbox_tasks = (
                    await inbox_task_uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.METRIC],
                        filter_metric_ref_ids=[m.ref_id for m in metrics],
                    )
                )

            for inbox_task in all_collection_inbox_tasks:
                async with progress_reporter.start_updating_entity(
                    "inbox task",
                    inbox_task.ref_id,
                    str(inbox_task.name),
                ) as entity_reporter:
                    async with self._domain_storage_engine.get_unit_of_work() as inbox_task_uow:
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
                        await entity_reporter.mark_known_name(str(inbox_task.name))

                        inbox_task = await inbox_task_uow.inbox_task_repository.save(
                            inbox_task,
                        )
                        await entity_reporter.mark_local_change()

        async with progress_reporter.start_updating_entity(
            "metric collection",
            metric_collection.ref_id,
            "Metric Collection",
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                metric_collection = metric_collection.change_collection_project(
                    collection_project_ref_id=collection_project_ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                await uow.metric_collection_repository.save(metric_collection)
                await entity_reporter.mark_local_change()
