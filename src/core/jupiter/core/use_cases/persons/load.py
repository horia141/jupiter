"""Use case for loading a person."""

from jupiter.core.domain.core.notes.infra.note_repository import NoteRepository
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.persons.person import Person
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
class PersonLoadArgs(UseCaseArgsBase):
    """PersonLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class PersonLoadResult(UseCaseResultBase):
    """PersonLoadResult."""

    person: Person
    catch_up_inbox_tasks: list[InboxTask]
    birthday_inbox_tasks: list[InboxTask]
    note: Note | None = None


@readonly_use_case(WorkspaceFeature.PERSONS)
class PersonLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[PersonLoadArgs, PersonLoadResult]
):
    """Use case for loading a person."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: PersonLoadArgs,
    ) -> PersonLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        person = await uow.get_for(Person).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )

        catch_up_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            person_ref_id=[args.ref_id],
            source=[InboxTaskSource.PERSON_CATCH_UP],
        )
        birthday_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            person_ref_id=[args.ref_id],
            source=[InboxTaskSource.PERSON_BIRTHDAY],
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.PERSON,
            person.ref_id,
            allow_archived=args.allow_archived,
        )

        return PersonLoadResult(
            person=person,
            catch_up_inbox_tasks=catch_up_inbox_tasks,
            birthday_inbox_tasks=birthday_inbox_tasks,
            note=note,
        )
