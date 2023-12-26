"""Use case for loading a metric entry."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
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
    note: Optional[Note] = None


@readonly_use_case(WorkspaceFeature.METRICS)
class MetricEntryLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[MetricEntryLoadArgs, MetricEntryLoadResult]
):
    """Use case for loading a metric entry."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: MetricEntryLoadArgs,
    ) -> MetricEntryLoadResult:
        """Execute the command's action."""
        metric_entry = await uow.metric_entry_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        note = await uow.note_repository.load_optional_for_source(
            NoteDomain.METRIC_ENTRY,
            metric_entry.ref_id,
            allow_archived=args.allow_archived,
        )

        return MetricEntryLoadResult(metric_entry=metric_entry, note=note)
