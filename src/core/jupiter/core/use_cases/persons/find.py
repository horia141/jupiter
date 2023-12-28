"""The command for finding the persons."""
from collections import defaultdict
from typing import List, Optional, cast

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
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
class PersonFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_catch_up_inbox_tasks: bool
    include_birthday_inbox_tasks: bool
    include_notes: bool
    filter_person_ref_ids: Optional[List[EntityId]] = None


@use_case_result_part
class PersonFindResultEntry:
    """A single person result."""

    person: Person
    catch_up_inbox_tasks: Optional[List[InboxTask]] = None
    birthday_inbox_tasks: Optional[List[InboxTask]] = None
    note: Note | None = None


@use_case_result
class PersonFindResult(UseCaseResultBase):
    """PersonFindResult."""

    catch_up_project: Project
    entries: List[PersonFindResultEntry]


@readonly_use_case(WorkspaceFeature.PERSONS)
class PersonFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[PersonFindArgs, PersonFindResult]
):
    """The command for finding the persons."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: PersonFindArgs,
    ) -> PersonFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        person_collection = await uow.person_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        catch_up_project = await uow.project_repository.load_by_id(
            person_collection.catch_up_project_ref_id,
        )
        persons = await uow.person_repository.find_all(
            parent_ref_id=person_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_person_ref_ids,
        )

        if args.include_catch_up_inbox_tasks:
            catch_up_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                    filter_person_ref_ids=(p.ref_id for p in persons),
                )
            )
        else:
            catch_up_inbox_tasks = None

        if args.include_birthday_inbox_tasks:
            birthday_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                    filter_person_ref_ids=(p.ref_id for p in persons),
                )
            )
        else:
            birthday_inbox_tasks = None

        all_notes_by_person_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            notes_collection = await uow.note_collection_repository.load_by_parent(
                workspace.ref_id
            )
            all_notes = await uow.note_repository.find_all_with_filters(
                parent_ref_id=notes_collection.ref_id,
                domain=NoteDomain.PERSON,
                allow_archived=True,
                filter_source_entity_ref_ids=[p.ref_id for p in persons],
            )
            for n in all_notes:
                all_notes_by_person_ref_id[cast(EntityId, n.source_entity_ref_id)] = n

        return PersonFindResult(
            catch_up_project=catch_up_project,
            entries=[
                PersonFindResultEntry(
                    person=p,
                    catch_up_inbox_tasks=[
                        it
                        for it in catch_up_inbox_tasks
                        if it.person_ref_id == p.ref_id
                    ]
                    if catch_up_inbox_tasks is not None
                    else None,
                    birthday_inbox_tasks=[
                        it
                        for it in birthday_inbox_tasks
                        if it.person_ref_id == p.ref_id
                    ]
                    if birthday_inbox_tasks is not None
                    else None,
                    note=all_notes_by_person_ref_id.get(p.ref_id, None),
                )
                for p in persons
            ],
        )
