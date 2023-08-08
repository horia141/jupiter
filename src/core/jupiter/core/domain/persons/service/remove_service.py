"""Remove a person."""
from typing import Final

from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.use_case import ProgressReporter


class PersonRemoveService:
    """The command for removing a person."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def do_it(
        self,
        progress_reporter: ProgressReporter,
        person_collection: PersonCollection,
        person: Person,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    person_collection.workspace_ref_id,
                )
            )
            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_person_ref_ids=[person.ref_id],
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine,
        )
        for inbox_task in all_inbox_tasks:
            await inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        async with self._storage_engine.get_unit_of_work() as uow:
            await uow.person_repository.remove(person.ref_id)
            await progress_reporter.mark_removed(person)
