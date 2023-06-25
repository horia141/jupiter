"""The command for updating a metric entry's properties."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricEntryUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    collection_time: UpdateAction[ADate]
    value: UpdateAction[float]
    notes: UpdateAction[Optional[str]]


class MetricEntryUpdateUseCase(AppLoggedInMutationUseCase[MetricEntryUpdateArgs, None]):
    """The command for updating a metric entry's properties."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_updating_entity(
            "metric entry",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                (
                    await uow.metric_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )
                metric_entry = await uow.metric_entry_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(metric_entry.simple_name))

                metric_entry = metric_entry.update(
                    collection_time=args.collection_time,
                    value=args.value,
                    notes=args.notes,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                await uow.metric_entry_repository.save(metric_entry)
                await entity_reporter.mark_known_name(str(metric_entry.simple_name))
                await entity_reporter.mark_local_change()
