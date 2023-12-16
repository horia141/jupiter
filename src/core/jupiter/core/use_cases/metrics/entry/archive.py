"""The command for archiving a metric entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class MetricEntryArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class MetricEntryArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricEntryArchiveArgs, None]
):
    """The command for archiving a metric entry."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        metric_entry = await uow.metric_entry_repository.load_by_id(args.ref_id)
        metric_entry = metric_entry.mark_archived(
            EventSource.CLI,
            self._time_provider.get_current_time(),
        )
        await uow.metric_entry_repository.save(metric_entry)
        await progress_reporter.mark_updated(metric_entry)

        note_archive_service = NoteArchiveService(EventSource.CLI, self._time_provider)
        await note_archive_service.archive_for_source(
            uow,
            NoteDomain.METRIC_ENTRY,
            metric_entry.ref_id,
        )
