"""The command for archiving a metric entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
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
class MetricEntryArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class MetricEntryArchiveUseCase(
    AppLoggedInMutationUseCase[MetricEntryArchiveArgs, None]
):
    """The command for archiving a metric entry."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.METRICS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_archiving_entity(
            "metric entry",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                metric_entry = await uow.metric_entry_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(metric_entry.simple_name))
                metric_entry = metric_entry.mark_archived(
                    EventSource.CLI,
                    self._time_provider.get_current_time(),
                )
                await uow.metric_entry_repository.save(metric_entry)
                await entity_reporter.mark_local_change()
