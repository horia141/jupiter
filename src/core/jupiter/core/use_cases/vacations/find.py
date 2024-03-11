"""The command for finding vacations."""
from collections import defaultdict

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class VacationFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_notes: bool
    filter_ref_ids: list[EntityId] | None = None


@use_case_result
class VacationFindResultEntry(UseCaseResultBase):
    """PersonFindResult object."""

    vacation: Vacation
    note: Note | None


@use_case_result
class VacationFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    entries: list[VacationFindResultEntry]


@readonly_use_case(WorkspaceFeature.VACATIONS)
class VacationFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[VacationFindArgs, VacationFindResult]
):
    """The command for finding vacations."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: VacationFindArgs,
    ) -> VacationFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        vacation_collection = await uow.get_for(VacationCollection).load_by_parent(
            workspace.ref_id,
        )
        vacations = await uow.get_for(Vacation).find_all(
            parent_ref_id=vacation_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        notes_by_vacation_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id,
            )
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.VACATION,
                allow_archived=True,
                source_entity_ref_id=[vacation.ref_id for vacation in vacations],
            )
            for note in notes:
                notes_by_vacation_ref_id[note.parent_ref_id] = note

        return VacationFindResult(
            entries=[
                VacationFindResultEntry(
                    vacation=vacation,
                    note=notes_by_vacation_ref_id.get(vacation.ref_id, None),
                )
                for vacation in vacations
            ]
        )
