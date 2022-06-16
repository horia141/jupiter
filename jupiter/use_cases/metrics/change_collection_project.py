"""Update the metrics collection project."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, cast

from jupiter.domain.adate import ADate
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricChangeCollectionProjectUseCase(
    AppMutationUseCase["MetricChangeCollectionProjectUseCase.Args", None]
):
    """The command for updating the collection up project for metrics."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        collection_project_key: Optional[ProjectKey]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        metric_notion_manager: MetricNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_notion_manager = metric_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )

            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            old_catch_up_project_ref_id = metric_collection.collection_project_ref_id

            if args.collection_project_key is not None:
                project = uow.project_repository.load_by_key(
                    project_collection.ref_id, args.collection_project_key
                )
                collection_project_ref_id = project.ref_id
            else:
                collection_project_ref_id = workspace.default_project_ref_id

            metric_collection = metric_collection.change_collection_project(
                collection_project_ref_id=collection_project_ref_id,
                source=EventSource.CLI,
                modified_time=self._time_provider.get_current_time(),
            )

            uow.metric_collection_repository.save(metric_collection)

            metrics = uow.metric_repository.find_all(
                parent_ref_id=metric_collection.ref_id, allow_archived=False
            )

        if (
            old_catch_up_project_ref_id != collection_project_ref_id
            and len(metrics) > 0
        ):
            LOGGER.info("Moving all inbox tasks too")
            with self._storage_engine.get_unit_of_work() as inbox_task_uow:
                inbox_task_collection = (
                    inbox_task_uow.inbox_task_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )
                all_collection_inbox_tasks = (
                    inbox_task_uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.METRIC],
                        filter_person_ref_ids=[m.ref_id for m in metrics],
                    )
                )
                for inbox_task in all_collection_inbox_tasks:
                    inbox_task.update_link_to_metric(
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
                    inbox_task_uow.inbox_task_repository.save(inbox_task)
