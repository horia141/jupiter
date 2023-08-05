"""The command for removing a metric entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricEntryRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class MetricEntryRemoveUseCase(AppLoggedInMutationUseCase[MetricEntryRemoveArgs, None]):
    """The command for removing a metric entry."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.METRICS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_removing_entity(
            "metric entry",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                metric_entry = await uow.metric_entry_repository.remove(args.ref_id)
                await entity_reporter.mark_known_name(str(metric_entry.name))
                await entity_reporter.mark_local_change()
