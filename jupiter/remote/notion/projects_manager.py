"""The centralised point for interacting with Notion projects."""
import logging
from typing import Final, ClassVar, Iterable

from notion.collection import CollectionRowBlock

from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager, NotionProjectNotFoundError
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import NotionClient, NotionCollectionSchemaProperties, NotionFieldProps, \
    NotionFieldShow
from jupiter.remote.notion.infra.collections_manager import NotionCollectionsManager, NotionCollectionItemNotFoundError
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionProjectsManager(ProjectNotionManager):
    """The centralised point for interacting with Notion projects."""

    _KEY: ClassVar[str] = "projects"
    _PAGE_NAME: ClassVar[str] = "Projects"
    _PAGE_ICON: ClassVar[str] = "💡"

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "key": {
            "name": "Key",
            "type": "text"
        },
        "last-edited-time": {
            "name": "Last Edited Time",
            "type": "last_edited_time"
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        }
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("key", NotionFieldShow.SHOW),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

    _DATABASE_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Database",
        "type": "table",
        "format": {
            "table_properties": [{
                "width": 300,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "key",
                "visible": True,
            }, {
                "width": 200,
                "property": "last-edited-time",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": False
            }]
        },
        "query2": {}
    }

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            collections_manager: NotionCollectionsManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._collections_manager = collections_manager

    def upsert_root_page(self, notion_workspace: NotionWorkspace, project_collection: NotionProjectCollection) -> None:
        """Upsert the root page for the projects section."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{project_collection.ref_id}"),
            parent_page_notion_id=notion_workspace.notion_id,
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                ("database_view_id", self._DATABASE_VIEW_SCHEMA)
            ])

    def upsert_project(self, project_collection_ref_id: EntityId, project: NotionProject) -> NotionProject:
        """Create a project."""
        link = \
            self._collections_manager.upsert_collection_item(
                key=NotionLockKey(f"{project.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"),
                new_row=project,
                copy_row_to_notion_row=self._copy_row_to_notion_row)
        return link.item_info

    def save_project(self, project_collection_ref_id: EntityId, project: NotionProject) -> NotionProject:
        """Update a Notion-side project with new data."""
        try:
            link = \
                self._collections_manager.save_collection_item(
                    key=NotionLockKey(f"{project.ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"),
                    row=project,
                    copy_row_to_notion_row=self._copy_row_to_notion_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionProjectNotFoundError(f"Project with id {project.ref_id} could not be found") from err

    def load_project(self, project_collection_ref_id: EntityId, ref_id: EntityId) -> NotionProject:
        """Load a Notion-side project."""
        try:
            link = \
                self._collections_manager.load_collection_item(
                    key=NotionLockKey(f"{ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionProjectNotFoundError(f"Project with id {ref_id} could not be found") from err

    def load_all_projects(self, project_collection_ref_id: EntityId) -> Iterable[NotionProject]:
        """Retrieve all the Notion-side project items."""
        return [l.item_info for l in
                self._collections_manager.load_all_collection_items(
                    collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)]

    def remove_project(self, project_collection_ref_id: EntityId, ref_id: EntityId) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"))
        except NotionCollectionItemNotFoundError as err:
            raise NotionProjectNotFoundError(f"Project with id {ref_id} could not be found") from err

    def drop_all_projects(self, project_collection_ref_id: EntityId) -> None:
        """Remove all projects Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"))

    def load_all_saved_project_ref_ids(self, project_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the projects."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"))

    def load_all_saved_project_notion_ids(self, project_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for the projects."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"))

    def link_local_and_notion_entries(
            self, project_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{project_collection_ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionProject, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.key = row.key
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = str(row.ref_id) if row.ref_id else None

        return notion_row

    def _copy_notion_row_to_row(self, project_notion_row: CollectionRowBlock) -> NotionProject:
        """Transform the live system data to something suitable for basic storage."""
        # pylint: disable=no-self-use
        return NotionProject(
            notion_id=NotionId.from_raw(project_notion_row.id),
            archived=False,
            name=project_notion_row.title,
            key=project_notion_row.key,
            last_edited_time=Timestamp.from_notion(project_notion_row.last_edited_time),
            ref_id=EntityId.from_raw(project_notion_row.ref_id) if project_notion_row.ref_id else None)
