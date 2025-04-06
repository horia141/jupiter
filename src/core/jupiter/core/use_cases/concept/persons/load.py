"""Use case for loading a person."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
    TimeEventFullDaysBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
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
    catch_up_task_retrieve_offset: int | None
    birthday_task_retrieve_offset: int | None


@use_case_result
class PersonLoadResult(UseCaseResultBase):
    """PersonLoadResult."""

    person: Person
    birthday_time_event_blocks: list[TimeEventFullDaysBlock]
    catch_up_tasks: list[InboxTask]
    catch_up_tasks_total_cnt: int
    catch_up_tasks_page_size: int
    birthday_tasks: list[InboxTask]
    birthday_tasks_total_cnt: int
    birthday_tasks_page_size: int
    note: Note | None


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
        if (
            args.catch_up_task_retrieve_offset is not None
            and args.catch_up_task_retrieve_offset < 0
        ):
            raise InputValidationError("Invalid catch_up_inbox_task_retrieve_offset")
        if (
            args.birthday_task_retrieve_offset is not None
            and args.birthday_task_retrieve_offset < 0
        ):
            raise InputValidationError("Invalid birthday_inbox_task_retrieve_offset")

        workspace = context.workspace
        person = await uow.get_for(Person).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.PERSON,
            person.ref_id,
            allow_archived=args.allow_archived,
        )
        birthday_time_event_blocks = await uow.get(
            TimeEventFullDaysBlockRepository
        ).find_for_namespace(
            TimeEventNamespace.PERSON_BIRTHDAY,
            person.ref_id,
            allow_archived=args.allow_archived,
        )

        catch_up_tasks_total_cnt = await uow.get(
            InboxTaskRepository
        ).count_all_for_source(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.PERSON_CATCH_UP,
            source_entity_ref_id=args.ref_id,
        )

        catch_up_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.PERSON_CATCH_UP,
            source_entity_ref_id=args.ref_id,
            retrieve_offset=args.catch_up_task_retrieve_offset or 0,
            retrieve_limit=InboxTaskRepository.PAGE_SIZE,
        )

        birthday_tasks_total_cnt = await uow.get(
            InboxTaskRepository
        ).count_all_for_source(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.PERSON_BIRTHDAY,
            source_entity_ref_id=args.ref_id,
        )

        birthday_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.PERSON_BIRTHDAY,
            source_entity_ref_id=args.ref_id,
            retrieve_offset=args.birthday_task_retrieve_offset or 0,
            retrieve_limit=InboxTaskRepository.PAGE_SIZE,
        )

        return PersonLoadResult(
            person=person,
            note=note,
            birthday_time_event_blocks=birthday_time_event_blocks,
            catch_up_tasks=catch_up_tasks,
            catch_up_tasks_total_cnt=catch_up_tasks_total_cnt,
            catch_up_tasks_page_size=InboxTaskRepository.PAGE_SIZE,
            birthday_tasks=birthday_tasks,
            birthday_tasks_total_cnt=birthday_tasks_total_cnt,
            birthday_tasks_page_size=InboxTaskRepository.PAGE_SIZE,
        )
