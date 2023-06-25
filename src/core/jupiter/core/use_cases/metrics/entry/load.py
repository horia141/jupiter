"""Use case for loading a metric entry."""
from dataclasses import dataclass

from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricEntryLoadArgs(UseCaseArgsBase):
    """MetricEntryLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class MetricEntryLoadResult(UseCaseResultBase):
    """MetricEntryLoadResult."""

    metric_entry: MetricEntry


class MetricEntryLoadUseCase(
    AppLoggedInReadonlyUseCase[MetricEntryLoadArgs, MetricEntryLoadResult]
):
    """Use case for loading a metric entry."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryLoadArgs,
    ) -> MetricEntryLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            metric_entry = await uow.metric_entry_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )

        return MetricEntryLoadResult(metric_entry=metric_entry)
