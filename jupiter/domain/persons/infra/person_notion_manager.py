"""A manager of Notion-side persons."""
from jupiter.domain.persons.notion_person import NotionPerson
from jupiter.domain.persons.notion_person_collection import NotionPersonCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.notion_manager import (
    NotionLeafEntityNotFoundError,
    ParentTrunkLeafNotionManager,
)


class NotionPersonNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion person was not found."""


class PersonNotionManager(
    ParentTrunkLeafNotionManager[NotionWorkspace, NotionPersonCollection, NotionPerson]
):
    """A manager of Notion-side persons."""
