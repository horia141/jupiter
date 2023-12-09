"""Use case for loading a metric entry."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.notes.note_source import NoteSource
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
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


class MetricEntryLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[MetricEntryLoadArgs, MetricEntryLoadResult]
):
    """Use case for loading a metric entry."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryLoadArgs,
    ) -> MetricEntryLoadResult:
        """Execute the command's action."""
        metric_entry = await uow.metric_entry_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        note = None
        if context.workspace.is_feature_available(WorkspaceFeature.NOTES):
            note = await uow.note_repository.load_optional_for_source(
                NoteSource.METRIC_ENTRY,
                metric_entry.ref_id,
                allow_archived=args.allow_archived,
            )

        return MetricEntryLoadResult(metric_entry=metric_entry, note=note)
