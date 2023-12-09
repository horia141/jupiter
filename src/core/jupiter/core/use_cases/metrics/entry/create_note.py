"""The command for creating a note for a metric entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class MetricEntryCreateNoteArgs(UseCaseArgsBase):
    """MetricEntryCreateNote args."""

    ref_id: EntityId


@dataclass
class MetricEntryCreateNoteResult(UseCaseResultBase):
    """MetricEntryCreate result."""

    new_note: Note


class MetricEntryCreateNoteUseCase(
    AppTransactionalLoggedInMutationUseCase[
        MetricEntryCreateNoteArgs, MetricEntryCreateNoteResult
    ],
):
    """The command for creating a metric entry note."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return [WorkspaceFeature.METRICS, WorkspaceFeature.NOTES]

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryCreateNoteArgs,
    ) -> MetricEntryCreateNoteResult:
        """Execute the command's action."""
        metric_entry = await uow.metric_entry_repository.load_by_id(args.ref_id)
        metric = await uow.metric_repository.load_by_id(metric_entry.metric_ref_id)
        note_collection = await uow.note_collection_repository.load_by_parent(
            context.workspace.ref_id
        )

        new_note = Note.new_note_for_metric_entry(
            note_collection_ref_id=note_collection.ref_id,
            metric_name=metric.name,
            metric_entry_ref_id=metric_entry.ref_id,
            collection_time=metric_entry.collection_time,
            content=[],
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        new_note = await uow.note_repository.create(new_note)
        await progress_reporter.mark_created(new_note)

        return MetricEntryCreateNoteResult(new_note=new_note)
