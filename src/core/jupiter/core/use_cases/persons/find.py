"""The command for finding the persons."""
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class PersonFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_catch_up_inbox_tasks: bool
    include_birthday_inbox_tasks: bool
    filter_person_ref_ids: Optional[List[EntityId]] = None


@dataclass
class PersonFindResultEntry:
    """A single person result."""

    person: Person
    catch_up_inbox_tasks: Optional[List[InboxTask]] = None
    birthday_inbox_tasks: Optional[List[InboxTask]] = None


@dataclass
class PersonFindResult(UseCaseResultBase):
    """PersonFindResult."""

    catch_up_project: Project
    entries: List[PersonFindResultEntry]


class PersonFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[PersonFindArgs, PersonFindResult]
):
    """The command for finding the persons."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PERSONS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
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
                )
                for p in persons
            ],
        )
