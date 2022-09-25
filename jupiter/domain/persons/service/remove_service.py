"""Remove a person."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.persons.infra.person_notion_manager import (
    PersonNotionManager,
    NotionPersonNotFoundError,
)
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus

LOGGER = logging.getLogger(__name__)


class PersonRemoveService:
    """The command for removing a person."""

    _storage_engine: Final[DomainStorageEngine]
    _person_notion_manager: Final[PersonNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        person_notion_manager: PersonNotionManager,
        inbox_task_notion_manager: InboxTaskNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._person_notion_manager = person_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(
        self,
        progress_reporter: ProgressReporter,
        person_collection: PersonCollection,
        person: Person,
    ) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                person_collection.workspace_ref_id
            )
            all_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_person_ref_ids=[person.ref_id],
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        for inbox_task in all_inbox_tasks:
            inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        with progress_reporter.start_removing_entity(
            "person", person.ref_id, str(person.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                uow.person_repository.remove(person.ref_id)
                entity_reporter.mark_local_change()

            try:
                self._person_notion_manager.remove_leaf(
                    person_collection.ref_id, person.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionPersonNotFoundError:
                LOGGER.info(
                    "Skipping removal on Notion side because person was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
