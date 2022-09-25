"""The service class for syncing the persons between local and Notion."""
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.notion_person import NotionPerson
from jupiter.domain.persons.notion_person_collection import NotionPersonCollection
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class PersonSyncService(
    TrunkLeafNotionSyncService[
        PersonCollection,
        Person,
        NotionWorkspace,
        NotionPersonCollection,
        NotionPerson,
        None,
        None,
    ]
):
    """The service class for syncing the persons between local and Notion."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        person_notion_manager: PersonNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            PersonCollection,
            Person,
            "person",
            NotionPerson,
            storage_engine,
            person_notion_manager,
        )
