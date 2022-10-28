"""The centralised point for interaction around all email tasks."""
from typing import Final, ClassVar, Optional, Iterable

from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
    NotionEmailTaskNotFoundError,
)
from jupiter.domain.push_integrations.email.notion_email_task import NotionEmailTask
from jupiter.domain.push_integrations.email.notion_email_task_collection import (
    NotionEmailTaskCollection,
)
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import (
    NotionCollectionSchemaProperties,
    NotionFieldProps,
    NotionFieldShow,
)
from jupiter.remote.notion.infra.collections_manager import (
    NotionCollectionsManager,
    NotionCollectionItemNotFoundError,
)
from jupiter.utils.global_properties import GlobalProperties


class NotionEmailTasksManager(EmailTaskNotionManager):
    """The centralised point for interacting with Notion email tasks."""

    _KEY: ClassVar[str] = "email-tasks"
    _PAGE_NAME: ClassVar[str] = "Email"
    _PAGE_ICON: ClassVar[str] = "📧"

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Subject",
            "type": "title",
            "alt-name": "subject",
            "alt-id": "subject",
        },
        "to-address": {"name": "To Address", "type": "text"},
        "body": {"name": "Body", "type": "text"},
        "archived": {"name": "Archived", "type": "checkbox"},
        "ref-id": {"name": "Ref Id", "type": "text"},
        "last-edited-time": {"name": "Last Edited Time", "type": "last_edited_time"},
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("to-address", NotionFieldShow.SHOW),
        NotionFieldProps("body", NotionFieldShow.SHOW),
        NotionFieldProps("archived", NotionFieldShow.HIDE),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

    _DATABASE_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Database",
        "type": "table",
        "format": {
            "table_properties": [
                {"width": 100, "property": "title", "visible": True},
                {"width": 100, "property": "to-address", "visible": True},
                {"width": 200, "property": "body", "visible": True},
                {"width": 100, "property": "archived", "visible": True},
                {"width": 100, "property": "ref-id", "visible": True},
                {"width": 100, "property": "last-edited-time", "visible": True},
            ]
        },
    }

    _global_properties: Final[GlobalProperties]
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
        self,
        global_properties: GlobalProperties,
        collections_manager: NotionCollectionsManager,
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._collections_manager = collections_manager

    def upsert_trunk(
        self, parent: NotionPushIntegrationGroup, trunk: NotionEmailTaskCollection
    ) -> None:
        """Upsert the Notion-side email task."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{trunk.ref_id}"),
            parent_page_notion_id=parent.notion_id,
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                ("database_view_id", NotionEmailTasksManager._DATABASE_VIEW_SCHEMA)
            ],
        )

    def upsert_leaf(
        self,
        trunk_ref_id: EntityId,
        leaf: NotionEmailTask,
    ) -> NotionEmailTask:
        """Upsert a email task."""
        link = self._collections_manager.upsert_collection_item(
            timezone=self._global_properties.timezone,
            schema=self._SCHEMA,
            key=NotionLockKey(f"{leaf.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            new_leaf=leaf,
        )
        return link.item_info

    def save_leaf(
        self,
        trunk_ref_id: EntityId,
        leaf: NotionEmailTask,
    ) -> NotionEmailTask:
        """Update the Notion-side email task with new data."""
        try:
            link = self._collections_manager.save_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                key=NotionLockKey(f"{leaf.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                row=leaf,
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionEmailTaskNotFoundError(
                f"Notion email task with id {leaf.ref_id} could not be found"
            ) from err

    def load_leaf(
        self, trunk_ref_id: EntityId, leaf_ref_id: EntityId
    ) -> NotionEmailTask:
        """Retrieve the Notion-side email task associated with a particular entity."""
        try:
            link = self._collections_manager.load_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionEmailTask,
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionEmailTaskNotFoundError(
                f"Notion email task with id {leaf_ref_id} could not be found"
            ) from err

    def load_all_leaves(self, trunk_ref_id: EntityId) -> Iterable[NotionEmailTask]:
        """Retrieve all the Notion-side email tasks."""
        return [
            l.item_info
            for l in self._collections_manager.load_all_collection_items(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionEmailTask,
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
        ]

    def remove_leaf(
        self, trunk_ref_id: EntityId, leaf_ref_id: Optional[EntityId]
    ) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
        except NotionCollectionItemNotFoundError as err:
            raise NotionEmailTaskNotFoundError(
                f"Notion email task with id {leaf_ref_id} could not be found"
            ) from err

    def drop_all_leaves(self, trunk_ref_id: EntityId) -> None:
        """Remove all email tasks Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the email tasks tasks."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def load_all_saved_notion_ids(self, trunk_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def link_local_and_notion_leaves(
        self, trunk_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId
    ) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id,
        )
