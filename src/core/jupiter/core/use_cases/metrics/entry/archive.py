"""The command for archiving a metric entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
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

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            metric_entry = await uow.metric_entry_repository.load_by_id(args.ref_id)
            metric_entry = metric_entry.mark_archived(
                EventSource.CLI,
                self._time_provider.get_current_time(),
            )
            await uow.metric_entry_repository.save(metric_entry)
            await progress_reporter.mark_updated(metric_entry)
