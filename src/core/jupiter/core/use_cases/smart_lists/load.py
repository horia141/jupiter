"""Use case for loading a smart list."""

from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class SmartListLoadArgs(UseCaseArgsBase):
    """SmartListLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class SmartListLoadResult(UseCaseResultBase):
    """SmartListLoadResult."""

    smart_list: SmartList
    note: Note | None
    smart_list_tags: list[SmartListTag]
    smart_list_items: list[SmartListItem]
    smart_list_item_notes: list[Note]


@readonly_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SmartListLoadArgs, SmartListLoadResult]
):
    """Use case for loading a smart list."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SmartListLoadArgs,
    ) -> SmartListLoadResult:
        """Execute the command's action."""
        smart_list = await uow.get_for(SmartList).load_by_id(
            args.ref_id,
            allow_archived=args.allow_archived,
        )
        smart_list_tags = await uow.get_for(SmartListTag).find_all_generic(
            parent_ref_id=smart_list.ref_id, allow_archived=args.allow_archived
        )
        smart_list_items = await uow.get_for(SmartListItem).find_all_generic(
            parent_ref_id=smart_list.ref_id, allow_archived=args.allow_archived
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.SMART_LIST,
            smart_list.ref_id,
            allow_archived=args.allow_archived,
        )

        note_collection = await uow.get_for(NoteCollection).load_by_parent(
            context.workspace.ref_id,
        )
        smart_list_item_notes = []
        if len(smart_list_items) > 0:
            smart_list_item_notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.SMART_LIST_ITEM,
                allow_archived=args.allow_archived,
                source_entity_ref_id=[item.ref_id for item in smart_list_items],
            )

        return SmartListLoadResult(
            smart_list=smart_list,
            note=note,
            smart_list_tags=smart_list_tags,
            smart_list_items=smart_list_items,
            smart_list_item_notes=smart_list_item_notes,
        )
