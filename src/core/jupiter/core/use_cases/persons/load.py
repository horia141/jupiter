"""Use case for loading a person."""
from dataclasses import dataclass

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.persons.person import Person
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class PersonLoadArgs(UseCaseArgsBase):
    """PersonLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class PersonLoadResult(UseCaseResultBase):
    """PersonLoadResult."""

    person: Person
    catch_up_inbox_tasks: list[InboxTask]
    birthday_inbox_tasks: list[InboxTask]


class PersonLoadUseCase(AppLoggedInReadonlyUseCase[PersonLoadArgs, PersonLoadResult]):
    """Use case for loading a person."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: PersonLoadArgs,
    ) -> PersonLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        async with self._storage_engine.get_unit_of_work() as uow:
            person = await uow.person_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            catch_up_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_person_ref_ids=[args.ref_id],
                    filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                )
            )
            birthday_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_person_ref_ids=[args.ref_id],
                    filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                )
            )

        return PersonLoadResult(
            person=person,
            catch_up_inbox_tasks=catch_up_inbox_tasks,
            birthday_inbox_tasks=birthday_inbox_tasks,
        )
