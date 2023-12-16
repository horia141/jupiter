"""The command for removing a metric entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class MetricEntryRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class MetricEntryRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricEntryRemoveArgs, None]
):
    """The command for removing a metric entry."""

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
        args: MetricEntryRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        metric_entry = await uow.metric_entry_repository.remove(args.ref_id)
        await progress_reporter.mark_removed(metric_entry)
        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            uow, NoteDomain.METRIC_ENTRY, metric_entry.ref_id
        )
