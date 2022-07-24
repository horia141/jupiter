"""The service class for syncing the VACATION database between local and Notion."""
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.notion_vacation import NotionVacation
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class VacationSyncService(
    TrunkLeafNotionSyncService[
        VacationCollection,
        Vacation,
        NotionWorkspace,
        NotionVacationCollection,
        NotionVacation,
        None,
        None,
    ]
):
    """The service class for syncing the vacations database between local and Notion."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        vacation_notion_manager: VacationNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            VacationCollection,
            Vacation,
            NotionVacation,
            storage_engine,
            vacation_notion_manager,
        )
