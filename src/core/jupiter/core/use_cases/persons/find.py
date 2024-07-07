"""The command for finding the persons."""
from collections import defaultdict
from typing import cast

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class PersonFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_catch_up_inbox_tasks: bool
    include_birthday_inbox_tasks: bool
    include_notes: bool
    filter_person_ref_ids: list[EntityId] | None


@use_case_result_part
class PersonFindResultEntry(UseCaseResultBase):
    """A single person result."""

    person: Person
    note: Note | None
    catch_up_inbox_tasks: list[InboxTask] | None
    birthday_inbox_tasks: list[InboxTask] | None


@use_case_result
class PersonFindResult(UseCaseResultBase):
    """PersonFindResult."""

    catch_up_project: Project
    entries: list[PersonFindResultEntry]


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

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        catch_up_project = await uow.get_for(Project).load_by_id(
            person_collection.catch_up_project_ref_id,
        )
        persons = await uow.get_for(Person).find_all(
            parent_ref_id=person_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_person_ref_ids,
        )

        if args.include_catch_up_inbox_tasks:
            catch_up_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.PERSON_CATCH_UP],
                person_ref_id=[p.ref_id for p in persons],
            )
        else:
            catch_up_inbox_tasks = None

        if args.include_birthday_inbox_tasks:
            birthday_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.PERSON_BIRTHDAY],
                person_ref_id=[p.ref_id for p in persons],
            )
        else:
            birthday_inbox_tasks = None

        all_notes_by_person_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            notes_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            all_notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=notes_collection.ref_id,
                domain=NoteDomain.PERSON,
                allow_archived=True,
                source_entity_ref_id=[p.ref_id for p in persons],
            )
            for n in all_notes:
                all_notes_by_person_ref_id[cast(EntityId, n.source_entity_ref_id)] = n

        return PersonFindResult(
            catch_up_project=catch_up_project,
            entries=[
                PersonFindResultEntry(
                    person=p,
                    note=all_notes_by_person_ref_id.get(p.ref_id, None),
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
                )
                for p in persons
            ],
        )
