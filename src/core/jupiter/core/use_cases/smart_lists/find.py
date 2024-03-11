"""The command for finding smart lists."""
from collections import defaultdict

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class SmartListFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_notes: bool
    include_tags: bool
    include_items: bool
    include_item_notes: bool
    filter_ref_ids: list[EntityId] | None = None
    filter_is_done: bool | None = None
    filter_tag_names: list[TagName] | None = None
    filter_tag_ref_id: list[EntityId] | None = None
    filter_item_ref_id: list[EntityId] | None = None


@use_case_result_part
class SmartListFindResponseEntry(UseCaseResultBase):
    """A single entry in the LoadAllSmartListsResponse."""

    smart_list: SmartList
    note: Note | None
    smart_list_tags: list[SmartListTag] | None = None
    smart_list_items: list[SmartListItem] | None = None
    smart_list_item_notes: list[Note] | None = None


@use_case_result
class SmartListFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    entries: list[SmartListFindResponseEntry]


@readonly_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SmartListFindArgs, SmartListFindResult]
):
    """The command for finding smart lists."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SmartListFindArgs,
    ) -> SmartListFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        smart_list_collection = await uow.get_for(SmartListCollection).load_by_parent(
            workspace.ref_id,
        )

        smart_lists = await uow.get_for(SmartList).find_all(
            parent_ref_id=smart_list_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        all_notes_by_smart_list_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id,
            )
            all_smart_list_notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.SMART_LIST,
                allow_archived=True,
                source_entity_ref_id=[sl.ref_id for sl in smart_lists],
            )
            for note in all_smart_list_notes:
                all_notes_by_smart_list_ref_id[note.source_entity_ref_id] = note

        if args.include_tags:
            smart_list_tags_by_smart_list_ref_ids = {}
            for smart_list in smart_lists:
                for smart_list_tag in await uow.get_for(SmartListTag).find_all_generic(
                    parent_ref_id=smart_list.ref_id,
                    allow_archived=args.allow_archived,
                    tag_name=args.filter_tag_names or NoFilter(),
                    ref_id=args.filter_tag_ref_id or NoFilter(),
                ):
                    if (
                        smart_list_tag.smart_list.ref_id
                        not in smart_list_tags_by_smart_list_ref_ids
                    ):
                        smart_list_tags_by_smart_list_ref_ids[
                            smart_list_tag.smart_list.ref_id
                        ] = [smart_list_tag]
                    else:
                        smart_list_tags_by_smart_list_ref_ids[
                            smart_list_tag.smart_list.ref_id
                        ].append(smart_list_tag)
        else:
            smart_list_tags_by_smart_list_ref_ids = None

        if args.include_items:
            smart_list_items_by_smart_list_ref_ids = {}
            for smart_list in smart_lists:
                for smart_list_item in await uow.get_for(
                    SmartListItem
                ).find_all_generic(
                    parent_ref_id=smart_list.ref_id,
                    allow_archived=args.allow_archived,
                    ref_id=args.filter_item_ref_id,
                    is_done=args.filter_is_done
                    if args.filter_is_done is not None
                    else NoFilter(),
                    tag_ref_id=args.filter_tag_ref_id or NoFilter(),
                ):
                    if (
                        smart_list_item.smart_list.ref_id
                        not in smart_list_items_by_smart_list_ref_ids
                    ):
                        smart_list_items_by_smart_list_ref_ids[
                            smart_list_item.smart_list.ref_id
                        ] = [smart_list_item]
                    else:
                        smart_list_items_by_smart_list_ref_ids[
                            smart_list_item.smart_list.ref_id
                        ].append(smart_list_item)
        else:
            smart_list_items_by_smart_list_ref_ids = None

        all_notes_by_smart_list_item_ref_id: defaultdict[EntityId, Note] = defaultdict(
            None
        )
        if args.include_item_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id,
            )
            all_smart_list_item_notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.SMART_LIST_ITEM,
                allow_archived=True,
            )
            for note in all_smart_list_item_notes:
                all_notes_by_smart_list_item_ref_id[note.source_entity_ref_id] = note

        return SmartListFindResult(
            entries=[
                SmartListFindResponseEntry(
                    smart_list=sl,
                    note=all_notes_by_smart_list_ref_id.get(sl.ref_id, None),
                    smart_list_tags=smart_list_tags_by_smart_list_ref_ids.get(
                        sl.ref_id,
                        [],
                    )
                    if smart_list_tags_by_smart_list_ref_ids is not None
                    else None,
                    smart_list_items=smart_list_items_by_smart_list_ref_ids.get(
                        sl.ref_id,
                        [],
                    )
                    if smart_list_items_by_smart_list_ref_ids is not None
                    else None,
                    smart_list_item_notes=list(
                        all_notes_by_smart_list_item_ref_id.values()
                    )
                    if args.include_item_notes
                    else None,
                )
                for sl in smart_lists
            ],
        )
