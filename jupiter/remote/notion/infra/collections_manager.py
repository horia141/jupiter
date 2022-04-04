"""The handler of collections on Notion side."""
import dataclasses
import hashlib
import logging
import typing
from copy import deepcopy
from typing import Callable, TypeVar, Final, Dict, Iterable, cast, List, Tuple

from notion.collection import CollectionRowBlock

from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.json import JSONDictType
from jupiter.framework.notion import NotionLeafEntity
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import (
    NotionClient,
    NotionCollectionSchemaProperties,
    NotionCollectionBlockNotFound,
    NotionCollectionRowNotFound,
)
from jupiter.remote.notion.infra.client_builder import NotionClientBuilder
from jupiter.remote.notion.infra.collection_field_tag_link import (
    NotionCollectionFieldTagLink,
    NotionCollectionFieldTagLinkExtra,
)
from jupiter.remote.notion.infra.collection_field_tag_link_repository import (
    NotionCollectionFieldTagLinkNotFoundError,
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
CopyRowToNotionRowT = Callable[
    [NotionClient, ItemT, CollectionRowBlock], CollectionRowBlock
]
CopyNotionRowToRowT = Callable[[CollectionRowBlock], ItemT]


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
        collection_key: NotionLockKey,
        key: NotionLockKey,
        new_row: ItemT,
        copy_row_to_notion_row: CopyRowToNotionRowT[ItemT],
    ) -> NotionCollectionItemLinkExtra[ItemT]:
        """Create a Notion entity."""
        if new_row.ref_id is None:
            raise Exception("Can only create over an entity which has a ref_id")
        if new_row.ref_id == BAD_REF_ID:
            raise Exception("Can only create over an entity which has a ref_id")

        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_key = self._build_compound_key(collection_key, key)
            item_link = uow.notion_collection_item_link_repository.load_optional(
                item_key
            )

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        was_found = False
        if item_link:
            notion_row = client.get_collection_row(collection, item_link.notion_id)
            if notion_row.alive:
                was_found = True
                LOGGER.info(
                    f"Entity already exists on Notion side with id={notion_row.id}"
                )

        if not was_found:
            notion_row = client.create_collection_row(collection)
            LOGGER.info(f"Created new row on Notion side with id={notion_row.id}")

        new_row = dataclasses.replace(new_row, notion_id=notion_row.id)

        if item_link:
            new_item_link = item_link.with_new_item(
                notion_row.id, self._time_provider.get_current_time()
            )
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_item_link_repository.save(new_item_link)
        else:
            new_item_link = NotionCollectionItemLink.new_notion_collection_item_link(
                key=item_key,
                collection_key=collection_key,
                ref_id=typing.cast(EntityId, new_row.ref_id),
                notion_id=notion_row.id,
                creation_time=self._time_provider.get_current_time(),
            )
            with self._storage_engine.get_unit_of_work() as uow:
                uow.notion_collection_item_link_repository.create(new_item_link)
        LOGGER.info("Saved local locks")

        copy_row_to_notion_row(client, new_row, notion_row)
        LOGGER.info(f"Created new entity with id {notion_row.id}")

        return new_item_link.with_extra(new_row)

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
        key: NotionLockKey,
        collection_key: NotionLockKey,
        row: ItemT,
        copy_row_to_notion_row: CopyRowToNotionRowT[ItemT],
    ) -> NotionCollectionItemLinkExtra[ItemT]:
        """Update the Notion-side entity with new data."""
        if row.ref_id is None or row.ref_id == BAD_REF_ID:
            raise Exception("Can only save over an entity which has a ref_id")

        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_key = self._build_compound_key(collection_key, key)
            try:
                item_link = uow.notion_collection_item_link_repository.load(item_key)
            except NotionCollectionItemLinkNotFoundError as err:
                raise NotionCollectionFieldTagNotFoundError(
                    f"Collection field tag with key {key} could not be found"
                ) from err

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        try:
            notion_row = client.get_collection_row(collection, item_link.notion_id)
        except NotionCollectionRowNotFound as err:
            raise NotionCollectionItemNotFoundError(
                f"Collection item with key {key} could not be found"
            ) from err

        copy_row_to_notion_row(client, row, notion_row)

        with self._storage_engine.get_unit_of_work() as uow:
            new_item_link = item_link.mark_update(
                self._time_provider.get_current_time()
            )
            uow.notion_collection_item_link_repository.save(new_item_link)

        return new_item_link.with_extra(row)

    def load_all_collection_items(
        self,
        collection_key: NotionLockKey,
        copy_notion_row_to_row: CopyNotionRowToRowT[ItemT],
    ) -> Iterable[NotionCollectionItemLinkExtra[ItemT]]:
        """Retrieve all the Notion-side entitys."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_links = (
                uow.notion_collection_item_link_repository.find_all_for_collection(
                    collection_key
                )
            )
        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )
        all_notion_rows = client.get_collection_all_rows(
            collection, collection_link.view_notion_ids["database_view_id"]
        )
        all_rows = [copy_notion_row_to_row(nr) for nr in all_notion_rows]
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
            for r in all_rows
        ]

    def load_collection_item(
        self,
        key: NotionLockKey,
        collection_key: NotionLockKey,
        copy_notion_row_to_row: CopyNotionRowToRowT[ItemT],
    ) -> NotionCollectionItemLinkExtra[ItemT]:
        """Retrieve the Notion-side entity associated with a particular entity."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_key = self._build_compound_key(collection_key, key)
            try:
                item_link = uow.notion_collection_item_link_repository.load(item_key)
            except NotionCollectionItemLinkNotFoundError as err:
                raise NotionCollectionItemNotFoundError(
                    f"Collection field tag with key {key} could not be found"
                ) from err

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        try:
            notion_row = client.get_collection_row(collection, item_link.notion_id)
        except NotionCollectionRowNotFound as err:
            raise NotionCollectionItemNotFoundError(
                f"Collection item with key {key} could not be found"
            ) from err

        return item_link.with_extra(copy_notion_row_to_row(notion_row))

    def remove_collection_item(
        self, key: NotionLockKey, collection_key: NotionLockKey
    ) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_key = self._build_compound_key(collection_key, key)
            try:
                item_link = uow.notion_collection_item_link_repository.load(item_key)
            except NotionCollectionItemLinkNotFoundError as err:
                raise NotionCollectionItemNotFoundError(
                    f"Collection field tag with key {key} could not be found"
                ) from err

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        try:
            notion_row = client.get_collection_row(collection, item_link.notion_id)
            notion_row.remove()
        except NotionCollectionRowNotFound as err:
            raise NotionCollectionItemNotFoundError(
                f"Collection item with key {key} could not be found"
            ) from err

        with self._storage_engine.get_unit_of_work() as uow:
            uow.notion_collection_item_link_repository.remove(item_key)

    def drop_all_collection_items(self, collection_key: NotionLockKey) -> None:
        """Hard remove all the Notion-side entities."""
        with self._storage_engine.get_unit_of_work() as uow:
            collection_link = uow.notion_collection_link_repository.load(collection_key)
            item_links = (
                uow.notion_collection_item_link_repository.find_all_for_collection(
                    collection_key
                )
            )

        client = self._client_builder.get_notion_client()
        collection = client.get_collection(
            collection_link.page_notion_id,
            collection_link.collection_notion_id,
            collection_link.view_notion_ids.values(),
        )

        all_notion_rows = client.get_collection_all_rows(
            collection, collection_link.view_notion_ids["database_view_id"]
        )

        for notion_row in all_notion_rows:
            notion_row.remove()

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
