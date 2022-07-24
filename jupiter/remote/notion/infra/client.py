"""A client for tailored interactions with Notion."""
import enum
import logging
from dataclasses import dataclass
from typing import Final, Optional, Iterable, List

from notion.block import (
    PageBlock,
    CollectionViewPageBlock,
    Block,
)
from notion.client import NotionClient as BaseNotionClient
from notion.collection import (
    CollectionView,
    Collection,
)

from jupiter.domain.remote.notion.space_id import NotionSpaceId
from jupiter.domain.remote.notion.token import NotionToken
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.json import JSONDictType

LOGGER = logging.getLogger(__name__)


class NotionPageBlockNotFound(Exception):
    """Error raised when a Notion page is not found."""


class NotionCollectionBlockNotFound(Exception):
    """Error raised when a Notion collection is not found."""


@dataclass(frozen=True)
class NotionClientConfig:
    """Configuration for the notion client."""

    space_id: NotionSpaceId
    token: NotionToken


@enum.unique
class NotionFieldShow(enum.Enum):
    """How to show a field in the details view in Notion."""

    SHOW = "show"
    HIDE = "hide"
    HIDE_IF_EMPTY = "hide_if_empty"


@dataclass()
class NotionFieldProps:
    """Properties of a field in a schema."""

    name: str
    show: NotionFieldShow


NotionCollectionSchemaProperties = List[NotionFieldProps]


class NotionClient:
    """A client for tailored interactions with Notion."""

    # _config: Final[NotionClientConfig]
    _client: Final[BaseNotionClient]

    def __init__(self, config: NotionClientConfig):
        """Constructor."""
        self._client = BaseNotionClient(token_v2=str(config.token))

    # Page structures.

    # 1.For big pages.

    def get_regular_page(self, page_id: NotionId) -> PageBlock:
        """Find a page from a space, with a given id."""
        the_block: Optional[Block] = self._client.get_block(str(page_id))
        if the_block is None:
            raise NotionPageBlockNotFound(
                f"A page block with id={page_id} could not be found"
            )
        if not isinstance(the_block, PageBlock):
            raise Exception(f"A block with id={page_id} is not a page")
        return the_block

    # 2.For collections.

    @staticmethod
    def create_collection_page(parent_page: PageBlock) -> CollectionViewPageBlock:
        """Create a collection page as a child of a given page."""
        collection_page = parent_page.children.add_new(CollectionViewPageBlock)
        return collection_page

    def get_collection_page_by_id(self, page_id: NotionId) -> CollectionViewPageBlock:
        """Retrieve an existing collection page."""
        collection_page = self._client.get_block(str(page_id))
        if collection_page is None:
            raise NotionCollectionBlockNotFound(
                f"A collection page with id={page_id} could not be found"
            )
        if not isinstance(collection_page, CollectionViewPageBlock):
            raise Exception(f"Page with id={page_id} is not a collection page")
        return collection_page

    def attach_view_to_collection_page(
        self,
        page: CollectionViewPageBlock,
        collection: Collection,
        view_id: Optional[NotionId],
        view_type: str,
        schema: JSONDictType,
    ) -> CollectionView:
        """Attach a view to a collection."""
        if view_id:
            view = self._client.get_collection_view(str(view_id), collection=collection)
            LOGGER.info(f"Found the collection {schema['name']} with view {view_id}")
        else:
            view = self._client.get_collection_view(
                self._client.create_record(
                    "collection_view", parent=page, type=view_type
                ),
                collection=collection,
            )
            view.set("collection_id", collection.id)
            LOGGER.info(f"Created the view {view_id} for collection {schema['name']}")

        view.name = schema["name"]
        self._client.submit_transaction(
            [
                {
                    "id": view.id,
                    "table": "collection_view",
                    "path": [],
                    "command": "update",
                    "args": schema,
                }
            ]
        )

        return view

    # 3.For other misc stuff.

    # Collections.

    def create_collection(
        self, collection_page: CollectionViewPageBlock, schema: JSONDictType
    ) -> Collection:
        """Create a collection for a given page and with a given schema."""
        collection = self._client.get_collection(
            self._client.create_record(
                "collection", parent=collection_page, schema=schema
            )
        )
        return collection

    def get_collection(
        self,
        collection_page_id: NotionId,
        collection_id: NotionId,
        all_view_ids: Iterable[NotionId],
    ) -> Collection:
        """Retrieve an existing collection."""
        collection_page = self.get_collection_page_by_id(collection_page_id)
        collection = collection_page.collection
        if collection.id != str(collection_id):
            raise Exception(
                f"Mismatch between page {collection.id} collection and selected one {collection_id}"
            )
        # Hack for notion-py. If we don't get all the collection views for a particular collection like this one
        # rather than just a single one, there's gonna be some deep code somewhere which will assume all of
        # them are present and croak! The code when you add an element to a collection, and you wanna assume
        # it's gonna be added to all view in some order!
        for view_id in all_view_ids:
            _ = self._client.get_collection_view(str(view_id), collection=collection)
        return collection

    def assign_collection_schema_properties(
        self,
        collection: Collection,
        schema_properties: NotionCollectionSchemaProperties,
    ) -> None:
        """Assign a particular field order to the collection."""
        self._client.submit_transaction(
            [
                {
                    "table": "collection",
                    "id": collection.id,
                    "path": ["format"],
                    "command": "update",
                    "args": {
                        "collection_page_properties": [
                            {"property": fo.name, "visible": False}
                            for fo in schema_properties
                        ]
                    },
                }
            ]
        )

        self._client.submit_transaction(
            [
                {
                    "table": "collection",
                    "id": collection.id,
                    "path": ["format"],
                    "command": "update",
                    "args": {
                        "property_visibility": [
                            {"property": fo.name, "visibility": fo.show.value}
                            for fo in schema_properties
                        ]
                    },
                }
            ]
        )
