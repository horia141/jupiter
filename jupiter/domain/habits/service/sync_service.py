"""The service class for dealing with habits."""
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class HabitSyncService(
    TrunkLeafNotionSyncService[
        HabitCollection,
        Habit,
        NotionWorkspace,
        NotionHabitCollection,
        NotionHabit,
        NotionHabit.DirectInfo,
        NotionHabit.InverseInfo,
    ]
):
    """The service class for dealing with habits."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        habit_notion_manager: HabitNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            HabitCollection, Habit, NotionHabit, storage_engine, habit_notion_manager
        )
