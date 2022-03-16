"""The command for updating a metric entry's properties."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class MetricEntryUpdateUseCase(AppMutationUseCase['MetricEntryUpdateUseCase.Args', None]):
    """The command for updating a metric entry's properties."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        collection_time: UpdateAction[ADate]
        value: UpdateAction[float]
        notes: UpdateAction[Optional[str]]

    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._notion_manager = notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = uow.metric_collection_repository.load_by_parent(workspace.ref_id)
            metric_entry = uow.metric_entry_repository.load_by_id(args.ref_id)

            metric_entry = metric_entry.update(
                collection_time=args.collection_time, value=args.value, notes=args.notes,
                source=EventSource.CLI, modification_time=self._time_provider.get_current_time())

            uow.metric_entry_repository.save(metric_entry)

        notion_metric_entry = \
            self._notion_manager.load_leaf(metric_collection.ref_id, metric_entry.metric_ref_id, metric_entry.ref_id)
        notion_metric_entry = notion_metric_entry.join_with_entity(metric_entry, None)
        self._notion_manager.save_leaf(metric_collection.ref_id, metric_entry.metric_ref_id, notion_metric_entry)
