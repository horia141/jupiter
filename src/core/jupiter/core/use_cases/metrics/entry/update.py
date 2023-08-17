"""The command for updating a metric entry's properties."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class MetricEntryUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    collection_time: UpdateAction[ADate]
    value: UpdateAction[float]
    notes: UpdateAction[Optional[str]]


class MetricEntryUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricEntryUpdateArgs, None]
):
    """The command for updating a metric entry's properties."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        metric_entry = await uow.metric_entry_repository.load_by_id(args.ref_id)

        metric_entry = metric_entry.update(
            collection_time=args.collection_time,
            value=args.value,
            notes=args.notes,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.metric_entry_repository.save(metric_entry)
        await progress_reporter.mark_updated(metric_entry)
