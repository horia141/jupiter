"""The service for dealing with lists."""
from remote.notion.common import NotionPageLink


class ListsService:
    """The service class for dealing with lists."""

    def __init__(self) -> None:
        """Constructor."""

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all lists will be linked to."""
