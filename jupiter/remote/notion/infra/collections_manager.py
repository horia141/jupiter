"""The handler of collections on Notion side."""
import dataclasses
import hashlib
import logging
import typing
from copy import deepcopy
from typing import TypeVar, Final, Dict, Iterable, cast, List, Tuple

from jupiter.domain.adate import ADate
from jupiter.domain.timezone import Timezone
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.notion_id import NotionId, BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.framework.notion import NotionLeafEntity
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import (
    NotionCollectionSchemaProperties,
    NotionCollectionBlockNotFound,
)
from jupiter.remote.notion.infra.client_builder import NotionClientBuilder
from jupiter.remote.notion.infra.client_v2 import (
    NotionCollectionItem,
    NotionBlock,
    NotionEntityNotFoundException,
)
from jupiter.remote.notion.infra.collection_field_tag_link import (
    NotionCollectionFieldTagLink,
    NotionCollectionFieldTagLinkExtra,
)
from jupiter.remote.notion.infra.collection_field_tag_link_repository import (
    NotionCollectionFieldTagLinkNotFoundError,
)
from jupiter.remote.notion.infra.collection_item_block_link import (
    NotionCollectionItemBlockLink,
)
from jupiter.remote.notion.infra.collection_item_link import (
    NotionCollectionItemLink,
    NotionCollectionItemLinkExtra,
)
from jupiter.remote.notion.infra.collection_item_link_repository import (
    NotionCollectionItemLinkNotFoundError,
)
from jupiter.remote.notion.infra.collection_link import (
    NotionCollectionLink,
    NotionCollectionLinkExtra,
)
from jupiter.remote.notion.infra.collection_link_repository import (
    NotionCollectionLinkNotFoundError,
)
from jupiter.remote.notion.infra.storage_engine import NotionStorageEngine
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionCollectionNotFoundError(Exception):
    """Error raised when a particular collection cannot be found."""


class NotionCollectionFieldTagNotFoundError(Exception):
    """Error raised when a particular collection field tag cannot be found."""


class NotionCollectionItemNotFoundError(Exception):
    """Error raised when a particular collection item cannot be found."""


ItemT = TypeVar("ItemT", bound=NotionLeafEntity[typing.Any, typing.Any, typing.Any])


class NotionCollectionsManager:
    """The handler for collections on Notion side."""

    _time_provider: Final[TimeProvider]
    _client_builder: Final[NotionClientBuilder]
    _storage_engine: Final[NotionStorageEngine]

    def __init__(
        self,
        time_provider: TimeProvider,
        client_builder: NotionClientBuilder,
        storage_engine: NotionStorageEngine,
    ) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._client_builder = client_builder
        self._storage_engine = storage_engine

    def upsert_collection(
        self,
        key: NotionLockKey,
        parent_page_notion_id: NotionId,
        name: str,
        icon: typing.Optional[str],
        schema: JSONDictType,
        schema_properties: NotionCollectionSchemaProperties,
        view_schemas: List[Tuple[str, JSONDictType]],
    ) -> NotionCollectionLinkExtra:
        """Create the Notion-side structure for this collection."""
        simdif_fields = set(schema.keys()).symmetric_difference(
            m.name for m in schema_properties
        )

        if len(simdif_fields) > 0:
            raise Exception(f"Schema params are off: {','.join(simdif_fields)}")

        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load_optional(key)

        client = self._client_builder.get_notion_client()

        if collection_link:
            page = client.get_collection_page_by_id(collection_link.page_notion_id)
            LOGGER.info(f"Found the already existing page as {page.id}")
            collection = client.get_collection(
                collection_link.page_notion_id,
                collection_link.collection_notion_id,
                collection_link.view_notion_ids.values(),
            )
            LOGGER.info(f"Found the already existing collection {collection.id}")
        else:
            page = client.create_collection_page(
                parent_page=client.get_regular_page(parent_page_notion_id)
            )
            LOGGER.info(f"Created the page as {page.id}")
            collection = client.create_collection(page, schema)
            LOGGER.info(f"Created the collection as {collection}")

        # Change the schema.

        old_schema = collection.get("schema")
        final_schema = self._merge_notion_schemas(old_schema, schema)
        collection.set("schema", final_schema)
        LOGGER.info("Applied the most current schema to the collection")

        # Attach the views.
        view_ids = collection_link.view_notion_ids if collection_link else {}
        for view_name, view_schema in view_schemas:
            the_view = client.attach_view_to_collection_page(
                page,
                collection,
                view_ids.get(view_name, None),
                cast(str, view_schema["type"]),
                view_schema,
            )
            view_ids[view_name] = the_view.id
            LOGGER.info(
                f"Attached view '{view_name}' to collection id='{collection.id}'"
            )

        # Tie everything up.

        page.set("collection_id", collection.id)
        page.set(
            "view_ids", [view_ids[view_name] for view_name, _ in view_schemas]
        )  # view_ids.values()))

        # Change the title.

        page.title = name
        page.icon = icon
        collection.name = name
        collection.set("icon", icon)
        LOGGER.info("Changed the name")

        # Arrange the fields.

        client.assign_collection_schema_properties(collection, schema_properties)
        LOGGER.info("Changed the field order")

        # Save local locks.
        if collection_link:
            new_notion_collection_link = collection_link.with_new_collection(
                page.id, collection.id, view_ids, self._time_provider.get_current_time()
            )
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_link_repository.save(new_notion_collection_link)
        else:
            new_notion_collection_link = (
                NotionCollectionLink.new_notion_collection_link(
                    key,
                    page.id,
                    collection.id,
                    view_ids,
                    self._time_provider.get_current_time(),
                )
            )
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_link_repository.create(new_notion_collection_link)
        LOGGER.info("Saved lock structure")

        return new_notion_collection_link.with_extra(name, icon)

    def save_collection(
        self,
        key: NotionLockKey,
        new_name: str,
        new_icon: typing.Optional[str],
        new_schema: JSONDictType,
    ) -> NotionCollectionLinkExtra:
        """Just updates the name and schema for the collection and asks no questions."""
        client = self._client_builder.get_notion_client()

        try:
            with self._storage_engine.get_unit_of_work() as uow:
                collection_link = uow.notion_collection_link_repository.load(key)
            page = client.get_collection_page_by_id(collection_link.page_notion_id)
            collection = client.get_collection(
                collection_link.page_notion_id,
                collection_link.collection_notion_id,
                collection_link.view_notion_ids.values(),
            )
        except (
            NotionCollectionLinkNotFoundError,
            NotionCollectionBlockNotFound,
        ) as err:
            raise NotionCollectionNotFoundError(
                f"Notion collection with key {key} cannot be found"
            ) from err

        page.title = new_name
        page.icon = new_icon
        collection.name = new_name
        collection.set("icon", new_icon)
        old_schema = collection.get("schema")
        final_schema = self._merge_notion_schemas(old_schema, new_schema)
        collection.set("schema", final_schema)
        LOGGER.info("Applied the most current schema to the collection")

        with self._storage_engine.get_unit_of_work() as uow:
            new_collection_link = collection_link.mark_update(
                self._time_provider.get_current_time()
            )
            uow.notion_collection_link_repository.save(new_collection_link)

        return new_collection_link.with_extra(new_name, new_icon)

    def save_collection_no_merge(
        self,
        key: NotionLockKey,
        new_name: str,
        new_icon: typing.Optional[str],
        new_schema: JSONDictType,
        newly_added_field: str,
    ) -> NotionCollectionLinkExtra:
        """Just updates the name and schema for the collection and asks no questions."""
        client = self._client_builder.get_notion_client()

        try:
            with self._storage_engine.get_unit_of_work() as uow:
                collection_link = uow.notion_collection_link_repository.load(key)
            page = client.get_collection_page_by_id(collection_link.page_notion_id)
            collection = client.get_collection(
                collection_link.page_notion_id,
                collection_link.collection_notion_id,
                collection_link.view_notion_ids.values(),
            )
        except (
            NotionCollectionLinkNotFoundError,
            NotionCollectionBlockNotFound,
        ) as err:
            raise NotionCollectionNotFoundError(
                f"Notion collection with key {key} cannot be found"
            ) from err

        page.title = new_name
        page.icon = new_icon
        collection.name = new_name
        collection.set("icon", new_icon)
        old_schema = collection.get("schema")
        final_schema = self._merge_notion_schemas(
            old_schema, new_schema, newly_added_field
        )
        collection.set("schema", final_schema)
        LOGGER.info("Applied the most current schema to the collection")

        with self._storage_engine.get_unit_of_work() as uow:
            new_collection_link = collection_link.mark_update(
                self._time_provider.get_current_time()
            )
            uow.notion_collection_link_repository.save(new_collection_link)

        return new_collection_link.with_extra(new_name, new_icon)

    def load_collection(self, key: NotionLockKey) -> NotionCollectionLinkExtra:
        """Retrive the Notion-side structure for this collection."""
        client = self._client_builder.get_notion_client()

        try:
            with self._storage_engine.get_unit_of_work() as uow:
                collection_link = uow.notion_collection_link_repository.load(key)
            page = client.get_collection_page_by_id(collection_link.page_notion_id)
            collection = client.get_collection(
                collection_link.page_notion_id,
                collection_link.collection_notion_id,
                collection_link.view_notion_ids.values(),
            )
        except (
            NotionCollectionLinkNotFoundError,
            NotionCollectionBlockNotFound,
        ) as err:
            raise NotionCollectionNotFoundError(
                f"Notion collection with key {key} cannot be found"
            ) from err
        return collection_link.with_extra(page.title, collection.get("icon"))

    def remove_collection(self, key: NotionLockKey) -> None:
        """Remove the Notion-side structure for this collection."""
        client = self._client_builder.get_notion_client()

        try:
            with self._storage_engine.get_unit_of_work() as uow:
                collection_link = uow.notion_collection_link_repository.load(key)
            page = client.get_collection_page_by_id(collection_link.page_notion_id)
            page.remove()
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_link_repository.remove(key)
        except (
            NotionCollectionLinkNotFoundError,
            NotionCollectionBlockNotFound,
        ) as err:
            raise NotionCollectionNotFoundError(
                f"Notion collection with key {key} cannot be found"
            ) from err

    def quick_update_view_for_collection(
        self, key: NotionLockKey, view_name: str, view_schema: JSONDictType
    ) -> None:
        """Update a single view for a collection."""
        client = self._client_builder.get_notion_client()

        try:
            with self._storage_engine.get_unit_of_work() as uow:
                collection_link = uow.notion_collection_link_repository.load(key)

            page = client.get_collection_page_by_id(collection_link.page_notion_id)
            collection = client.get_collection(
                collection_link.page_notion_id,
                collection_link.collection_notion_id,
                collection_link.view_notion_ids.values(),
            )

            # Change the view schema.
            view_ids = collection_link.view_notion_ids if collection_link else {}
            client.attach_view_to_collection_page(
                page,
                collection,
                view_ids[view_name],
                cast(str, view_schema["type"]),
                view_schema,
            )
            LOGGER.info(
                f"Attached view '{view_name}' to collection id='{collection.id}'"
            )
        except (
            NotionCollectionLinkNotFoundError,
            NotionCollectionBlockNotFound,
        ) as err:
            raise NotionCollectionNotFoundError(
                f"Notion collection with key {key} cannot be found"
            ) from err

    @staticmethod
    def _build_compound_key(collection_key: str, key: str) -> NotionLockKey:
        return NotionLockKey(f"{collection_key}:{key}")

    def upsert_collection_field_tag(
        self,
        collection_key: NotionLockKey,
        key: NotionLockKey,
        ref_id: EntityId,
        field: str,
        tag: str,
    ) -> NotionCollectionFieldTagLinkExtra:
        """Create a new tag for a Collection's field which has tags support."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            tag_key = self._build_compound_key(collection_key, key)
            field_tag_link = (
                uow.notion_collection_field_tag_link_repository.load_optional(tag_key)
            )

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            field_schema["options"] = []

        tag_id = None
        if field_tag_link:
            for option in field_schema["options"]:
                if option["id"] == str(field_tag_link.notion_id):
                    option["value"] = tag
                    option["color"] = self._get_stable_color(tag_key)
                    tag_id = field_tag_link.notion_id
                    LOGGER.info(
                        f'Found tag "{tag}" ({field_tag_link.notion_id}) for field "{field}"'
                    )
                    break
            else:
                LOGGER.info(f'Could not find "{tag}" ({field_tag_link.notion_id})')

        if tag_id is None:
            tag_id = NotionId.make_brand_new()
            field_schema["options"].append(
                {
                    "id": str(tag_id),
                    "value": tag,
                    "color": self._get_stable_color(tag_key),
                }
            )
            LOGGER.info("Added new item for collection schema")

        collection.set("schema", schema)

        if field_tag_link:
            new_field_tag_link = field_tag_link.with_new_tag(
                tag_id, self._time_provider.get_current_time()
            )
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_field_tag_link_repository.save(new_field_tag_link)
        else:
            new_field_tag_link = (
                NotionCollectionFieldTagLink.new_notion_collection_field_tag_link(
                    tag_key,
                    collection_key,
                    field,
                    ref_id,
                    tag_id,
                    self._time_provider.get_current_time(),
                )
            )
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_field_tag_link_repository.create(
                    new_field_tag_link
                )
        LOGGER.info("Saved lock structure")

        return new_field_tag_link.with_extra(tag)

    def quick_link_local_and_notion_collection_field_tag(
        self,
        key: NotionLockKey,
        collection_key: NotionLockKey,
        field: str,
        ref_id: EntityId,
        notion_id: NotionId,
    ) -> NotionCollectionFieldTagLink:
        """Link a local entity with the Notion one, useful in syncing processes."""
        tag_key = self._build_compound_key(collection_key, key)

        with self._storage_engine.get_unit_of_work() as uow:
            field_tag_link = (
                uow.notion_collection_field_tag_link_repository.load_optional(tag_key)
            )

            if field_tag_link is not None:
                LOGGER.warning(
                    f"Entity already exists on Notion side for entity with id={ref_id}"
                )
                new_field_tag_link = field_tag_link.with_new_tag(
                    notion_id, self._time_provider.get_current_time()
                )
                uow.notion_collection_field_tag_link_repository.save(new_field_tag_link)
            else:
                new_field_tag_link = (
                    NotionCollectionFieldTagLink.new_notion_collection_field_tag_link(
                        key=tag_key,
                        collection_key=collection_key,
                        field=field,
                        ref_id=ref_id,
                        notion_id=notion_id,
                        creation_time=self._time_provider.get_current_time(),
                    )
                )
                uow.notion_collection_field_tag_link_repository.create(
                    new_field_tag_link
                )

        return new_field_tag_link

    def save_collection_field_tag(
        self, collection_key: NotionLockKey, key: NotionLockKey, field: str, tag: str
    ) -> NotionCollectionFieldTagLinkExtra:
        """Create a new tag for a Collection's field which has tags support."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            tag_key = self._build_compound_key(collection_key, key)
            try:
                field_tag_link = uow.notion_collection_field_tag_link_repository.load(
                    tag_key
                )
            except NotionCollectionFieldTagNotFoundError as err:
                raise NotionCollectionFieldTagNotFoundError(
                    f"Collection field tag with key {key} could not be found"
                ) from err

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            field_schema["options"] = []

        for option in field_schema["options"]:
            if option["id"] == str(field_tag_link.notion_id):
                option["value"] = tag
                option["color"] = self._get_stable_color(tag_key)
                LOGGER.info(
                    f'Found tag "{tag}" ({field_tag_link.notion_id}) for field "{field}"'
                )
                break
        else:
            raise NotionCollectionFieldTagNotFoundError(
                f'Could not find "{tag}" ({field_tag_link.notion_id})'
            )

        collection.set("schema", schema)

        with self._storage_engine.get_unit_of_work() as uow:
            new_field_tag_link = field_tag_link.mark_update(
                self._time_provider.get_current_time()
            )
            uow.notion_collection_field_tag_link_repository.save(new_field_tag_link)

        return new_field_tag_link.with_extra(tag)

    def load_collection_field_tag(
        self,
        collection_key: NotionLockKey,
        key: NotionLockKey,
        ref_id: EntityId,
        field: str,
    ) -> NotionCollectionFieldTagLinkExtra:
        """Load a particular tag for a field in a collection."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            tag_key = self._build_compound_key(collection_key, key)
            try:
                field_tag_link = uow.notion_collection_field_tag_link_repository.load(
                    tag_key
                )
            except NotionCollectionFieldTagLinkNotFoundError as err:
                raise NotionCollectionFieldTagNotFoundError(
                    f"Collection field tag with key {key} could not be found"
                ) from err

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            field_schema["options"] = []

        for option in field_schema["options"]:
            if option["id"] == str(field_tag_link.notion_id):
                return field_tag_link.with_extra(option["value"])

        raise NotionCollectionFieldTagNotFoundError(
            f"Could not find tag with id {ref_id} ({field_tag_link.notion_id})"
        )

    def load_all_collection_field_tags(
        self, collection_key: NotionLockKey, field: str
    ) -> Iterable[NotionCollectionFieldTagLinkExtra]:
        """Load all tags for a field in a collection."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            field_tag_links = (
                uow.notion_collection_field_tag_link_repository.find_all_for_collection(
                    collection_key, field
                )
            )

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            return []

        tag_links_lock_by_tag_id = {str(s.notion_id): s for s in field_tag_links}
        return [
            tag_links_lock_by_tag_id[tl["id"]].with_extra(tl["value"])
            if tl["id"] in tag_links_lock_by_tag_id
            else NotionCollectionFieldTagLink.new_notion_collection_field_tag_link(
                key=self._build_compound_key(
                    collection_key, NotionLockKey("just-found")
                ),
                collection_key=collection_key,
                field=field,
                ref_id=BAD_REF_ID,
                notion_id=tl["id"],
                creation_time=self._time_provider.get_current_time(),
            ).with_extra(tl["value"])
            for tl in field_schema["options"]
        ]

    def remove_collection_field_tag(
        self, key: NotionLockKey, collection_key: NotionLockKey
    ) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            tag_key = self._build_compound_key(collection_key, key)
            try:
                field_tag_link = uow.notion_collection_field_tag_link_repository.load(
                    tag_key
                )
            except NotionCollectionFieldTagNotFoundError as err:
                raise NotionCollectionFieldTagNotFoundError(
                    f"Collection field tag with key {key} could not be found"
                ) from err
        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        schema = collection.get("schema")

        if field_tag_link.field not in schema:
            raise Exception(f'Field "{field_tag_link.field}" not in schema')

        field_schema = schema[field_tag_link.field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(
                f'Field "{field_tag_link.field}" is not appropriate for tags'
            )

        if "options" not in field_schema:
            field_schema["options"] = []

        for option_idx, option in enumerate(field_schema["options"]):
            if option["id"] == str(field_tag_link.notion_id):
                del field_schema["options"][option_idx]
                LOGGER.info(
                    f'Found tag {field_tag_link.notion_id} for field "{field_tag_link.field}"'
                )
                break
        else:
            raise NotionCollectionFieldTagNotFoundError(
                f"Cannot find collection field tag with key {key}"
            )

        collection.set("schema", schema)

        with self._storage_engine.get_unit_of_work() as uow:
            uow.notion_collection_field_tag_link_repository.remove(tag_key)

    def drop_all_collection_field_tags(
        self, collection_key: NotionLockKey, field: str
    ) -> None:
        """Hard remove all the Notion-side entities."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load_optional(
                collection_key
            )
            if collection_link is None:
                return
            field_tag_links = (
                uow.notion_collection_field_tag_link_repository.find_all_for_collection(
                    collection_key, field
                )
            )

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        field_schema["options"] = []

        collection.set("schema", schema)

        with self._storage_engine.get_unit_of_work() as uow:
            for field_tag_link in field_tag_links:
                uow.notion_collection_field_tag_link_repository.remove(
                    field_tag_link.key
                )

    def load_all_saved_collection_field_tag_notion_ids(
        self, collection_key: NotionLockKey, field: str
    ) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids."""
        with self._storage_engine.get_unit_of_work() as uow:
            return [
                ftl.notion_id
                for ftl in uow.notion_collection_field_tag_link_repository.find_all_for_collection(
                    collection_key, field
                )
            ]

    def upsert_collection_item(
        self,
        timezone: Timezone,
        schema: JSONDictType,
        collection_key: NotionLockKey,
        key: NotionLockKey,
        new_leaf: ItemT,
        no_properties_fields: typing.Optional[Iterable[str]] = None,
        content_block: typing.Optional[NotionBlock] = None,
    ) -> NotionCollectionItemLinkExtra[ItemT]:
        """Create a Notion entity."""
        if new_leaf.ref_id is None:
            raise Exception("Can only create over an entity which has a ref_id")
        if new_leaf.ref_id == BAD_REF_ID:
            raise Exception("Can only create over an entity which has a ref_id")

        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_key = self._build_compound_key(collection_key, key)
            item_link = uow.notion_collection_item_link_repository.load_optional(
                item_key
            )
            block_links = (
                uow.notion_collection_item_block_link_repository.find_all_for_item(
                    item_key
                )
            )

        client = self._client_builder.get_notion_client_v2()

        was_found = False
        if item_link is not None:
            collection_item = client.get_collection_item(item_link.notion_id)
            if not collection_item.archived:
                was_found = True
                LOGGER.info(
                    f"Entity already exists on Notion side with id={collection_item.notion_id}"
                )

        # This logic is so annoying!
        if item_link and was_found:
            if len(block_links) == 1:
                if content_block is None:
                    client.remove_content_block(block_links[0].notion_id)
                    new_content_block = None
                else:
                    if content_block.__class__.__name__ != block_links[0].the_type:
                        client.remove_content_block(block_links[0].notion_id)
                        new_content_block = client.create_content_block(
                            item_link.notion_id, content_block
                        )
                    else:
                        new_content_block = client.update_content_block(
                            content_block.assign_notion_id(block_links[0].notion_id)
                        )
            elif content_block is not None:
                new_content_block = client.create_content_block(
                    item_link.notion_id, content_block
                )
            else:
                new_content_block = None

            collection_item = self._transform_leaf_into_collection_item(
                timezone=timezone,
                schema=schema,
                notion_id=item_link.notion_id,
                database_notion_id=collection_link.page_notion_id,
                created_time=item_link.created_time,
                item=new_leaf,
                content_block=new_content_block,
                no_properties_fields=no_properties_fields,
            )
            collection_item = client.update_collection_item(collection_item)
        else:
            collection_item = self._transform_leaf_into_collection_item(
                timezone=timezone,
                schema=schema,
                notion_id=BAD_NOTION_ID,
                database_notion_id=collection_link.page_notion_id,
                created_time=self._time_provider.get_current_time(),
                item=new_leaf,
                content_block=content_block,
                no_properties_fields=no_properties_fields,
            )
            collection_item = client.create_collection_item(collection_item)

        new_leaf = dataclasses.replace(new_leaf, notion_id=collection_item.notion_id)

        with self._storage_engine.get_unit_of_work() as uow:
            if item_link:
                new_item_link = item_link.with_new_item(
                    collection_item.notion_id, self._time_provider.get_current_time()
                )
                uow.notion_collection_item_link_repository.save(new_item_link)

                if len(block_links) == 1:
                    if collection_item.content_block is None:
                        uow.notion_collection_item_block_link_repository.remove(
                            item_key, 0
                        )
                    else:
                        updated_content_block_link = block_links[0].with_new_item(
                            collection_item.content_block.notion_id,
                            collection_item.content_block.__class__.__name__,
                            self._time_provider.get_current_time(),
                        )
                        uow.notion_collection_item_block_link_repository.save(
                            updated_content_block_link
                        )
                elif collection_item.content_block is not None:
                    new_content_block_link = NotionCollectionItemBlockLink.new(
                        the_type=collection_item.content_block.__class__.__name__,
                        position=0,
                        item_key=item_key,
                        collection_key=collection_key,
                        notion_id=collection_item.content_block.notion_id,
                        creation_time=self._time_provider.get_current_time(),
                    )
                    uow.notion_collection_item_block_link_repository.create(
                        new_content_block_link
                    )
            else:
                new_item_link = (
                    NotionCollectionItemLink.new_notion_collection_item_link(
                        key=item_key,
                        collection_key=collection_key,
                        ref_id=typing.cast(EntityId, new_leaf.ref_id),
                        notion_id=collection_item.notion_id,
                        creation_time=self._time_provider.get_current_time(),
                    )
                )
                uow.notion_collection_item_link_repository.create(new_item_link)

                if collection_item.content_block is not None:
                    new_content_block_link = NotionCollectionItemBlockLink.new(
                        the_type=collection_item.content_block.__class__.__name__,
                        position=0,
                        item_key=item_key,
                        collection_key=collection_key,
                        notion_id=collection_item.content_block.notion_id,
                        creation_time=self._time_provider.get_current_time(),
                    )
                    uow.notion_collection_item_block_link_repository.create(
                        new_content_block_link
                    )

        return new_item_link.with_extra(new_leaf)

    def quick_link_local_and_notion_entries_for_collection_item(
        self,
        key: NotionLockKey,
        collection_key: NotionLockKey,
        ref_id: EntityId,
        notion_id: NotionId,
    ) -> NotionCollectionItemLink:
        """Link a local entity with the Notion one, useful in syncing processes."""
        item_key = self._build_compound_key(collection_key, key)

        with self._storage_engine.get_unit_of_work() as uow:
            item_link = uow.notion_collection_item_link_repository.load_optional(
                item_key
            )

            if item_link is not None:
                new_item_link = item_link.with_new_item(
                    notion_id, self._time_provider.get_current_time()
                )
                LOGGER.warning(
                    f"Entity already exists on Notion side for entity with id={ref_id}"
                )
                uow.notion_collection_item_link_repository.save(new_item_link)
            else:
                new_item_link = (
                    NotionCollectionItemLink.new_notion_collection_item_link(
                        key=item_key,
                        collection_key=collection_key,
                        ref_id=ref_id,
                        notion_id=notion_id,
                        creation_time=self._time_provider.get_current_time(),
                    )
                )
                uow.notion_collection_item_link_repository.create(new_item_link)

        return new_item_link

    def save_collection_item(
        self,
        timezone: Timezone,
        schema: JSONDictType,
        key: NotionLockKey,
        collection_key: NotionLockKey,
        row: ItemT,
        no_properties_fields: typing.Optional[Iterable[str]] = None,
        content_block: typing.Optional[NotionBlock] = None,
    ) -> NotionCollectionItemLinkExtra[ItemT]:
        """Update the Notion-side entity with new data."""
        if row.ref_id is None or row.ref_id == BAD_REF_ID:
            raise Exception("Can only save over an entity which has a ref_id")

        try:
            with self._storage_engine.get_unit_of_work() as uow:
                collection_link = uow.notion_collection_link_repository.load(
                    collection_key
                )
                item_key = self._build_compound_key(collection_key, key)
                item_link = uow.notion_collection_item_link_repository.load(item_key)
                block_links = (
                    uow.notion_collection_item_block_link_repository.find_all_for_item(
                        item_key
                    )
                )

            client = self._client_builder.get_notion_client_v2()

            collection_item = self._transform_leaf_into_collection_item(
                timezone=timezone,
                schema=schema,
                notion_id=item_link.notion_id,
                database_notion_id=collection_link.page_notion_id,
                created_time=item_link.created_time,
                item=row,
                no_properties_fields=no_properties_fields,
            )

            client.update_collection_item(collection_item)

            if len(block_links) == 1:
                if content_block is None:
                    client.remove_content_block(block_links[0].notion_id)
                    new_content_block = None
                else:
                    if content_block.__class__.__name__ != block_links[0].the_type:
                        client.remove_content_block(block_links[0].notion_id)
                        new_content_block = client.create_content_block(
                            item_link.notion_id, content_block
                        )
                    else:
                        new_content_block = client.update_content_block(
                            content_block.assign_notion_id(block_links[0].notion_id)
                        )
            elif content_block is not None:
                new_content_block = client.create_content_block(
                    item_link.notion_id, content_block
                )
            else:
                new_content_block = None

            with self._storage_engine.get_unit_of_work() as uow:
                new_item_link = item_link.mark_update(
                    self._time_provider.get_current_time()
                )
                uow.notion_collection_item_link_repository.save(new_item_link)

                if len(block_links) == 1:
                    if new_content_block is None:
                        uow.notion_collection_item_block_link_repository.remove(
                            item_key, 0
                        )
                    else:
                        updated_content_block_link = block_links[0].with_new_item(
                            new_content_block.notion_id,
                            new_content_block.__class__.__name__,
                            self._time_provider.get_current_time(),
                        )
                        uow.notion_collection_item_block_link_repository.save(
                            updated_content_block_link
                        )
                elif new_content_block is not None:
                    new_content_block_link = NotionCollectionItemBlockLink.new(
                        the_type=new_content_block.__class__.__name__,
                        position=0,
                        item_key=item_key,
                        collection_key=collection_key,
                        notion_id=new_content_block.notion_id,
                        creation_time=self._time_provider.get_current_time(),
                    )
                    uow.notion_collection_item_block_link_repository.create(
                        new_content_block_link
                    )

            return new_item_link.with_extra(row)
        except (
            NotionCollectionItemLinkNotFoundError,
            NotionEntityNotFoundException,
        ) as err:
            raise NotionCollectionFieldTagNotFoundError(
                f"Collection field tag with key {key} could not be found"
            ) from err

    def load_all_collection_items(
        self,
        timezone: Timezone,
        schema: JSONDictType,
        ctor: typing.Type[ItemT],
        collection_key: NotionLockKey,
        no_properties_fields: typing.Optional[Iterable[str]] = None,
    ) -> Iterable[NotionCollectionItemLinkExtra[ItemT]]:
        """Retrieve all the Notion-side entitys."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_links = (
                uow.notion_collection_item_link_repository.find_all_for_collection(
                    collection_key
                )
            )
        client = self._client_builder.get_notion_client_v2()
        collection_items_gen = list(
            client.find_all_collection_items(collection_link.page_notion_id)
        )
        leaves = [
            self._transform_collection_item_into_leaf(
                timezone, schema, ctor, ci, no_properties_fields
            )
            for ci in collection_items_gen
        ]
        all_item_links_by_notion_id = {il.notion_id: il for il in item_links}

        return [
            (
                all_item_links_by_notion_id[r.notion_id].with_extra(r)
                if r.notion_id in all_item_links_by_notion_id
                else NotionCollectionItemLink.new_notion_collection_item_link(
                    key=self._build_compound_key(
                        collection_key, NotionLockKey("just-found")
                    ),
                    collection_key=collection_key,
                    ref_id=BAD_REF_ID,
                    notion_id=r.notion_id,
                    creation_time=self._time_provider.get_current_time(),
                ).with_extra(r)
            )
            for r in leaves
        ]

    def load_collection_item(
        self,
        timezone: Timezone,
        schema: JSONDictType,
        ctor: typing.Type[ItemT],
        key: NotionLockKey,
        collection_key: NotionLockKey,
        no_properties_fields: typing.Optional[Iterable[str]] = None,
    ) -> NotionCollectionItemLinkExtra[ItemT]:
        """Retrieve the Notion-side entity associated with a particular entity."""
        try:
            item_key = self._build_compound_key(collection_key, key)

            with self._storage_engine.get_unit_of_work() as uow:
                item_link = uow.notion_collection_item_link_repository.load(item_key)

            client = self._client_builder.get_notion_client_v2()
            collection_item = client.get_collection_item(item_link.notion_id)

            leaf = self._transform_collection_item_into_leaf(
                timezone, schema, ctor, collection_item, no_properties_fields
            )

            return item_link.with_extra(leaf)
        except (
            NotionCollectionItemLinkNotFoundError,
            NotionEntityNotFoundException,
        ) as err:
            raise NotionCollectionItemNotFoundError(
                f"Collection item with key {key} could not be found"
            ) from err

    def remove_collection_item(
        self, key: NotionLockKey, collection_key: NotionLockKey
    ) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            with self._storage_engine.get_unit_of_work() as uow:
                item_key = self._build_compound_key(collection_key, key)
                item_link = uow.notion_collection_item_link_repository.load(item_key)

            client = self._client_builder.get_notion_client_v2()
            client.remove_collection_item(item_link.notion_id)

            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_item_link_repository.remove(item_key)
                uow.notion_collection_item_block_link_repository.remove_all_for_item(
                    item_key
                )
        except (
            NotionCollectionItemLinkNotFoundError,
            NotionEntityNotFoundException,
        ) as err:
            raise NotionCollectionItemNotFoundError(
                f"Collection item with key {key} could not be found"
            ) from err

    def drop_all_collection_items(self, collection_key: NotionLockKey) -> None:
        """Hard remove all the Notion-side entities."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load_optional(
                collection_key
            )
            if collection_link is None:
                return
            item_links = (
                uow.notion_collection_item_link_repository.find_all_for_collection(
                    collection_key
                )
            )

        client = self._client_builder.get_notion_client_v2()
        for collection_item in client.find_all_collection_items(
            collection_link.page_notion_id
        ):
            client.remove_collection_item(collection_item.notion_id)

        with self._storage_engine.get_unit_of_work() as uow:
            for item_link in item_links:
                uow.notion_collection_item_link_repository.remove(item_link.key)

    def load_all_collection_items_saved_notion_ids(
        self, collection_key: NotionLockKey
    ) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids."""
        with self._storage_engine.get_unit_of_work() as uow:
            return [
                r.notion_id
                for r in uow.notion_collection_item_link_repository.find_all_for_collection(
                    collection_key
                )
            ]

    def load_all_collection_items_saved_ref_ids(
        self, collection_key: NotionLockKey
    ) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids."""
        with self._storage_engine.get_unit_of_work() as uow:
            return [
                r.ref_id
                for r in uow.notion_collection_item_link_repository.find_all_for_collection(
                    collection_key
                )
            ]

    def _transform_leaf_into_collection_item(
        self,
        timezone: Timezone,
        schema: JSONDictType,
        notion_id: NotionId,
        database_notion_id: NotionId,
        created_time: Timestamp,
        item: ItemT,
        content_block: typing.Optional[NotionBlock] = None,
        no_properties_fields: typing.Optional[typing.Iterable[str]] = None,
    ) -> NotionCollectionItem:
        # This method transforms a regular Leaf into a properties dictionary
        # than can then be used to feed into Notion.
        # Big assumption is that `item` is flat!

        properties: JSONDictType = {}
        schema_alt_ids: typing.Any = {s["alt-id"]: v for v, s in schema.items() if "alt-id" in s}  # type: ignore

        for field in dataclasses.fields(item):
            field_name = field.name
            field_value = item.__dict__[field_name]

            if field_name in ("notion_id", "last_edited_time"):
                continue
            if no_properties_fields is not None and field_name in no_properties_fields:
                continue
            if field_name == "name":
                field_name_notion = "title"
            else:
                field_name_notion = field_name.replace("_", "-")
            if (
                field_name_notion not in schema
                and field_name_notion not in schema_alt_ids
            ):
                raise RuntimeError(
                    f"Could not map item field {field_name} to any one in the schema"
                )
            if field_name_notion in schema:
                field_desc: typing.Any = schema[field_name_notion]  # type: ignore
            else:
                field_desc: typing.Any = schema[schema_alt_ids[field_name_notion]]  # type: ignore
            if field_desc["type"] == "title":
                if not isinstance(field_value, str):
                    raise RuntimeError(f"Trying to map {field_name} to title")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "title",
                    "title": [
                        {
                            "annotations": {
                                "bold": False,
                                "code": False,
                                "color": "default",
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                            },
                            "href": None,
                            "plain_text": field_value,
                            "text": {"content": field_value, "link": None},
                            "type": "text",
                        }
                    ],
                }
            elif field_desc["type"] == "select":
                if field_value is not None and not isinstance(field_value, str):
                    raise RuntimeError(f"Trying to map {field_name} to select")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "select",
                    "select": {"name": field_value} if field_value else None,
                }
            elif field_desc["type"] == "multi_select":
                if not isinstance(field_value, list):
                    raise RuntimeError(f"Trying to map {field_name} to multi select")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "multi_select",
                    "multi_select": [{"name": fv} for fv in field_value],
                }
            elif field_desc["type"] == "text":
                if field_value is not None and not isinstance(
                    field_value, (str, EntityId)
                ):
                    raise RuntimeError(f"Trying to map {field_name} to text")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "rich_text",
                    "rich_text": [
                        {
                            "annotations": {
                                "bold": False,
                                "code": False,
                                "color": "default",
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                            },
                            "href": None,
                            "plain_text": str(field_value),
                            "text": {"content": str(field_value), "link": None},
                            "type": "text",
                        }
                    ]
                    if field_value
                    else [],
                }
            elif field_desc["type"] == "date":
                if field_value is not None and not isinstance(field_value, ADate):
                    raise RuntimeError(f"Trying to map {field_name} to date")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "date",
                    "date": {
                        "end": None,
                        "start": ADate.to_user_str(timezone, field_value)
                        if field_value
                        else None,
                        "time_zone": str(timezone)
                        if field_value and field_value.has_time
                        else None,
                    }
                    if field_value
                    else None,
                }
            elif field_desc["type"] == "checkbox":
                if not isinstance(field_value, bool):
                    raise RuntimeError(f"Trying to map {field_name} to boolean")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "checkbox",
                    "checkbox": field_value,
                }
            elif field_desc["type"] == "number":
                if field_value is not None and not isinstance(
                    field_value, (int, float)
                ):
                    raise RuntimeError(f"Trying to map {field_name} to number")
                properties[field_desc["name"]] = {
                    "id": field_name_notion,
                    "type": "number",
                    "number": field_value,
                }
            else:
                raise RuntimeError(f"Unknown field type {field_desc['type']}")

        return NotionCollectionItem(
            notion_id=notion_id,
            database_notion_id=database_notion_id,
            archived=False,
            properties=properties,
            content_block=content_block,
            created_time=created_time,
            last_edited_time=self._time_provider.get_current_time(),
        )

    @staticmethod
    def _transform_collection_item_into_leaf(
        timezone: Timezone,
        schema: JSONDictType,
        ctor: typing.Type[ItemT],
        collection_item: NotionCollectionItem,
        no_properties_fields: typing.Optional[Iterable[str]] = None,
    ) -> ItemT:
        # This method transforms a properties dictionary into a leaf.
        # Assumes that the leaf is flat, or has well-known primitive types.
        fields: typing.Any = {
            "notion_id": collection_item.notion_id,
            "last_edited_time": collection_item.last_edited_time,
        }  # type: ignore

        if no_properties_fields:
            for field_name in no_properties_fields:
                fields[field_name] = None

        for field_value_any in collection_item.properties.values():
            field_value: typing.Any = field_value_any  # type: ignore
            field_id = field_value["id"]
            if field_id not in schema:
                raise RuntimeError(f"Unrecognized field {field_id}")
            if field_id == "last-edited-time":
                continue
            if "alt-name" in typing.cast(JSONDictType, schema[field_id]):
                field_name = cast(str, cast(typing.Any, schema)[field_id]["alt-name"])  # type: ignore
            elif field_id == "title":
                field_name = "name"
            else:
                field_name = field_id.replace("-", "_")
            if field_value["type"] == "title":
                fields[field_name] = (
                    field_value["title"][0]["plain_text"]
                    if len(field_value["title"]) > 0
                    else None
                )
            elif field_value["type"] == "select":
                fields[field_name] = (
                    field_value["select"]["name"] if field_value["select"] else None
                )
            elif field_value["type"] == "multi_select":
                fields[field_name] = [fi["name"] for fi in field_value["multi_select"]]
            elif field_value["type"] == "rich_text":
                value = (
                    field_value["rich_text"][0]["plain_text"]
                    if len(field_value["rich_text"]) > 0
                    else None
                )
                if field_id == "ref-id" and value is not None:
                    fields[field_name] = EntityId.from_raw(value)
                else:
                    fields[field_name] = value
            elif field_value["type"] == "date":
                fields[field_name] = (
                    ADate.from_raw(timezone, field_value["date"]["start"])
                    if field_value["date"] and field_value["date"]["start"]
                    else None
                )
            elif field_value["type"] == "checkbox":
                fields[field_name] = field_value["checkbox"]
            elif field_value["type"] == "number":
                fields[field_name] = field_value["number"]
            else:
                raise RuntimeError(f"Unknown field type {field_value}")

        return ctor(**fields)

    @staticmethod
    def _merge_notion_schemas(
        old_schema: JSONDictType,
        new_schema: JSONDictType,
        newly_added_field: typing.Optional[str] = None,
    ) -> JSONDictType:
        """Merge an old and new schema for the collection."""
        old_schema_any: typing.Any = old_schema  # type: ignore
        new_schema_any: typing.Any = new_schema  # type: ignore
        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        # As another special case, the recurring tasks group key is left to whatever value it had
        # before since this thing is managed by the other flows!
        for (schema_item_name, schema_item) in new_schema_any.items():
            if schema_item_name == newly_added_field:
                combined_schema[schema_item_name] = schema_item
            elif schema_item_name in ("bigplan2", "project-name"):
                combined_schema[schema_item_name] = (
                    old_schema_any[schema_item_name]
                    if (
                        schema_item_name in old_schema_any
                        and old_schema_any[schema_item_name]["type"] == "select"
                    )
                    else schema_item
                )
            elif (
                schema_item["type"] == "select" or schema_item["type"] == "multi_select"
            ):
                if schema_item_name in old_schema_any:
                    old_v = old_schema_any[schema_item_name]

                    combined_schema[schema_item_name] = {
                        "name": schema_item["name"],
                        "type": schema_item["type"],
                        "options": deepcopy(schema_item["options"]),
                    }

                    old_options = typing.cast(
                        typing.List[Dict[str, str]], old_v.get("options", [])
                    )
                    for option in combined_schema[schema_item_name]["options"]:
                        for old_option in old_options:
                            if option["value"] == old_option["value"]:
                                option["id"] = old_option["id"]
                                break
                else:
                    combined_schema[schema_item_name] = schema_item
            else:
                combined_schema[schema_item_name] = schema_item

        return combined_schema

    @staticmethod
    def _get_stable_color(option_id: str) -> str:
        """Return a random-ish yet stable color for a given name."""
        colors = [
            "gray",
            "brown",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "red",
        ]
        return colors[
            hashlib.sha256(option_id.encode("utf-8")).digest()[0] % len(colors)
        ]
