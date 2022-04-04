"""The command for hard removing a metric."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricRemoveUseCase(AppMutationUseCase["MetricRemoveUseCase.Args", None]):
    """The command for removing a metric."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        key: MetricKey

    _metric_notion_manager: Final[MetricNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

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
        self._metric_notion_manager = metric_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            metric = uow.metric_repository.load_by_key(
                metric_collection.ref_id, args.key
            )

        MetricRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._metric_notion_manager,
        ).execute(metric_collection, metric)
