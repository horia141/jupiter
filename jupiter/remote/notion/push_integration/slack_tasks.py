"""The centralised point for interaction around all Slack tasks."""
import logging
from typing import Final, ClassVar, Optional, Iterable

from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
    NotionSlackTaskNotFoundError,
)
from jupiter.domain.push_integrations.slack.notion_slack_task import NotionSlackTask
from jupiter.domain.push_integrations.slack.notion_slack_task_collection import (
    NotionSlackTaskCollection,
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

LOGGER = logging.getLogger(__name__)


class NotionSlackTasksManager(SlackTaskNotionManager):
    """The centralised point for interacting with Notion slack tasks."""

    _KEY: ClassVar[str] = "slack-tasks"
    _PAGE_NAME: ClassVar[str] = "Slack"
    _PAGE_ICON: ClassVar[str] = "💬"

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {"name": "User", "type": "title"},
        "channel": {"name": "Channel", "type": "text"},
        "message": {"name": "Message", "type": "text"},
        "extra-info": {
            "name": "Extra Info",
            "type": "text",
            "alt-id": "generation-extra-info",
            "alt-name": "generation_extra_info",
        },
        "archived": {"name": "Archived", "type": "checkbox"},
        "ref-id": {"name": "Ref Id", "type": "text"},
        "last-edited-time": {"name": "Last Edited Time", "type": "last_edited_time"},
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("channel", NotionFieldShow.SHOW),
        NotionFieldProps("message", NotionFieldShow.SHOW),
        NotionFieldProps("extra-info", NotionFieldShow.SHOW),
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
                {"width": 100, "property": "channel", "visible": True},
                {"width": 200, "property": "message", "visible": True},
                {"width": 200, "property": "extra-info", "visible": True},
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
        self, parent: NotionPushIntegrationGroup, trunk: NotionSlackTaskCollection
    ) -> None:
        """Upsert the Notion-side slack task."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{trunk.ref_id}"),
            parent_page_notion_id=parent.notion_id,
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                ("database_view_id", NotionSlackTasksManager._DATABASE_VIEW_SCHEMA)
            ],
        )

    def upsert_leaf(
        self,
        trunk_ref_id: EntityId,
        leaf: NotionSlackTask,
    ) -> NotionSlackTask:
        """Upsert a slack task."""
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
        leaf: NotionSlackTask,
    ) -> NotionSlackTask:
        """Update the Notion-side slack task with new data."""
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
            raise NotionSlackTaskNotFoundError(
                f"Notion slack task with id {leaf.ref_id} could not be found"
            ) from err

    def load_leaf(
        self, trunk_ref_id: EntityId, leaf_ref_id: EntityId
    ) -> NotionSlackTask:
        """Retrieve the Notion-side slack task associated with a particular entity."""
        try:
            link = self._collections_manager.load_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionSlackTask,
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionSlackTaskNotFoundError(
                f"Notion slack task with id {leaf_ref_id} could not be found"
            ) from err

    def load_all_leaves(self, trunk_ref_id: EntityId) -> Iterable[NotionSlackTask]:
        """Retrieve all the Notion-side slack tasks."""
        return [
            l.item_info
            for l in self._collections_manager.load_all_collection_items(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionSlackTask,
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
            raise NotionSlackTaskNotFoundError(
                f"Notion slack task with id {leaf_ref_id} could not be found"
            ) from err

    def drop_all_leaves(self, trunk_ref_id: EntityId) -> None:
        """Remove all slack tasks Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the slack tasks tasks."""
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
