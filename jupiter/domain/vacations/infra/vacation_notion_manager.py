"""A manager of Notion-side vacations."""
from jupiter.domain.vacations.notion_vacation import NotionVacation
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.notion_manager import (
    NotionLeafEntityNotFoundError,
    ParentTrunkLeafNotionManager,
)


class NotionVacationNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion vacation was not found."""


class VacationNotionManager(
    ParentTrunkLeafNotionManager[
        NotionWorkspace, NotionVacationCollection, NotionVacation
    ]
):
    """A manager of Notion-side vacations."""
