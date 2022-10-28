"""A correct Notion client."""
import dataclasses
import time
from dataclasses import dataclass
from typing import Optional, ClassVar, Iterable, TypeVar, cast, Any, Final

import requests

from jupiter.domain.remote.notion.api_token import NotionApiToken
from jupiter.domain.timezone import UTC
from jupiter.framework.base.notion_id import NotionId, BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType

_NotionBlockT = TypeVar("_NotionBlockT", bound="NotionBlock")


class NotionClientException(Exception):
    """Exception raised when interacting with Notion."""


class NotionEntityNotFoundException(NotionClientException):
    """Exception raised when an entity that should exist doesn't."""


@dataclass(frozen=True)
class NotionBlock:
    """A block on Notion side."""

    notion_id: NotionId

    def assign_notion_id(self: _NotionBlockT, notion_id: NotionId) -> _NotionBlockT:
        """Assign a Notion id to the entity."""
        return dataclasses.replace(self, notion_id=notion_id)

    def to_create_form(self) -> JSONDictType:
        """Representation for the API create methods."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def to_update_form(self) -> JSONDictType:
        """Representation for the API update methods."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


@dataclass(frozen=True)
class NotionTextBlock(NotionBlock):
    """A text block on Notion side."""

    text: str

    def to_create_form(self) -> JSONDictType:
        """Representation for the API create methods."""
        return {
            "object": "block",
            "type": "paragraph",
            "archived": False,
            "paragraph": {
                "color": "default",
                "rich_text": [
                    {
                        "type": "text",
                        "plain_text": self.text,
                        "text": {"content": self.text, "link": None},
                    }
                ],
            },
        }

    def to_update_form(self) -> JSONDictType:
        """Representation for the API update methods."""
        return self.to_create_form()


@dataclass(frozen=True)
class NotionRootPage:
    """A root page on Notion side."""

    notion_id: NotionId
    name: str
    icon: Optional[str]


@dataclass(frozen=True)
class NotionRegularPage:
    """A page on Notion side."""

    notion_id: NotionId
    parent_page_notion_id: NotionId
    name: str
    icon: Optional[str]

    @staticmethod
    def new(
        parent_page_notion_id: NotionId, name: str, icon: Optional[str]
    ) -> "NotionRegularPage":
        """Construct a new page."""
        return NotionRegularPage(
            notion_id=BAD_NOTION_ID,
            parent_page_notion_id=parent_page_notion_id,
            name=name,
            icon=icon,
        )

    def assign_notion_id(self, notion_id: NotionId) -> "NotionRegularPage":
        """Assign a Notion id to the entity."""
        return dataclasses.replace(self, notion_id=notion_id)


@dataclass(frozen=True)
class NotionCollectionItem:
    """A collection item on Notion side."""

    notion_id: NotionId
    database_notion_id: NotionId
    archived: bool
    properties: JSONDictType
    content_block: Optional[NotionBlock]
    created_time: Timestamp
    last_edited_time: Timestamp

    def assign_notion_id(
        self, notion_id: NotionId, content_block: Optional[NotionBlock]
    ) -> "NotionCollectionItem":
        """Assign a Notion id to the entity."""
        return dataclasses.replace(
            self, notion_id=notion_id, content_block=content_block
        )


@dataclass(frozen=True)
class NotionClientV2Config:
    """Config for the Notion client."""

    api_token: NotionApiToken


class NotionClientV2:
    """A correct Notion client."""

    _API_ROOT: ClassVar[str] = "https://api.notion.com/v1"
    _API_VERSION: ClassVar[str] = "2022-02-22"
    _FIND_API_PAGE_SIZE: ClassVar[int] = 100
    _WAIT_TIME_BETWEEN_RATE_LIMIT_RETRIES_MS: ClassVar[int] = 1000
    _MAX_RATE_LIMIT_RETRIES: ClassVar[int] = 5

    _config: Final[NotionClientV2Config]

    def __init__(self, config: NotionClientV2Config) -> None:
        """Ctor."""
        self._config = config

    def get_root_page(self, page_id: NotionId) -> NotionRootPage:
        """Retrieve the basic information about a root page."""
        url = f"{NotionClientV2._API_ROOT}/pages/{page_id}"
        json_data = self._get(url)

        if json_data["parent"]["type"] != "workspace":
            raise Exception("Trying to retrieve something which isn't a root page")

        name = json_data["properties"]["title"]["title"][0]["plain_text"]

        icon = None
        if json_data["icon"]["type"] == "emoji":
            icon = json_data["icon"]["emoji"]

        return NotionRootPage(
            notion_id=page_id,
            name=name,
            icon=icon,
        )

    def create_regular_page(self, page: NotionRegularPage) -> NotionRegularPage:
        """Create a page on Notion side."""
        url = f"{NotionClientV2._API_ROOT}/pages"
        payload = {
            "icon": {"type": "emoji", "emoji": page.icon} if page.icon else None,
            "parent": {"type": "page_id", "page_id": str(page.parent_page_notion_id)},
            "properties": {
                "title": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": page.name, "link": None},
                            "plain_text": page.name,
                            "href": None,
                        }
                    ],
                }
            },
        }

        json_data = self._post(url, payload)

        return page.assign_notion_id(NotionId.from_raw(json_data["id"]))

    def update_regular_page(self, page: NotionRegularPage) -> NotionRegularPage:
        """Update a page."""
        url = f"{NotionClientV2._API_ROOT}/pages/{page.notion_id}"
        payload = {
            "icon": {"type": "emoji", "emoji": page.icon} if page.icon else None,
            "properties": {
                "title": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": page.name, "link": None},
                            "plain_text": page.name,
                            "href": None,
                        }
                    ],
                }
            },
        }

        self._patch(url, payload)

        return page

    def get_regular_page(self, page_id: NotionId) -> NotionRegularPage:
        """Retrieve the basic information about a page."""
        url = f"{NotionClientV2._API_ROOT}/pages/{page_id}"
        json_data = self._get(url)

        if json_data["parent"]["type"] != "page_id":
            raise Exception("Trying to retrieve something which isn't a regular page")

        name = json_data["properties"]["title"]["title"][0]["plain_text"]

        icon = None
        if json_data["icon"]["type"] == "emoji":
            icon = json_data["icon"]["emoji"]

        return NotionRegularPage(
            notion_id=page_id,
            parent_page_notion_id=NotionId.from_raw(json_data["parent"]["page_id"]),
            name=name,
            icon=icon,
        )

    def remove_regular_page(self, page_id: NotionId) -> None:
        """Remove a particular page."""
        url = f"{NotionClientV2._API_ROOT}/blocks/{page_id}"
        self._delete(url)

    def create_collection_item(
        self,
        collection_item: NotionCollectionItem,
    ) -> NotionCollectionItem:
        """Create a new collection item."""
        if collection_item.notion_id != BAD_NOTION_ID:
            raise Exception(
                "Attempting to create a collection item which already exists"
            )
        if collection_item.content_block is not None:
            if collection_item.content_block.notion_id != BAD_NOTION_ID:
                raise Exception("Attempting to create a block which already exists")

        url = f"{NotionClientV2._API_ROOT}/pages"
        payload = {
            "parent": {
                "type": "database_id",
                "database_id": str(collection_item.database_notion_id),
            },
            "properties": collection_item.properties,
        }
        if collection_item.content_block:
            payload["children"] = [collection_item.content_block.to_create_form()]

        json_data = self._post(url, payload)

        notion_id = NotionId.from_raw(json_data["id"])

        if collection_item.content_block is not None:
            children_url = f"{self._API_ROOT}/blocks/{notion_id}/children?page_size={self._FIND_API_PAGE_SIZE}"
            children_json = self._get(children_url)

            # test some errors here

            if len(children_json["results"]) != 1:
                raise Exception(
                    f"Something's not right --> {len(children_json['results'])} != 1"
                )

            result_child = children_json["results"][0]
            if result_child["type"] == "paragraph" and isinstance(
                collection_item.content_block, NotionTextBlock
            ):
                new_content_block = collection_item.content_block.assign_notion_id(
                    NotionId.from_raw(result_child["id"])
                )
            else:
                raise Exception(
                    f"Unknown block type {result_child['type']} matched with {collection_item.content_block.__class__.__name__}"
                )
        else:
            new_content_block = None

        return collection_item.assign_notion_id(notion_id, new_content_block)

    def update_collection_item(
        self, collection_item: NotionCollectionItem
    ) -> NotionCollectionItem:
        """Update a particular item."""
        if collection_item.notion_id == BAD_NOTION_ID:
            raise Exception(
                "Attempting to create a collection item which does not exist"
            )
        url = f"{NotionClientV2._API_ROOT}/pages/{collection_item.notion_id}"
        payload = {"properties": collection_item.properties}

        self._patch(url, payload)

        return collection_item

    def find_all_collection_items(
        self, database_id: NotionId
    ) -> Iterable[NotionCollectionItem]:
        """Retrieve all collection items in a particular database."""
        url = f"{NotionClientV2._API_ROOT}/databases/{database_id}/query"

        payload = {"page_size": self._FIND_API_PAGE_SIZE}

        while True:
            json_data = self._post(url, payload)

            has_more = json_data["has_more"]
            payload["start_cursor"] = json_data["next_cursor"]

            for result_item in json_data["results"]:
                if result_item["archived"]:
                    continue
                yield NotionCollectionItem(
                    notion_id=NotionId.from_raw(result_item["id"]),
                    database_notion_id=database_id,
                    archived=result_item["archived"],
                    properties=result_item["properties"],
                    content_block=None,
                    created_time=Timestamp.from_raw(UTC, result_item["created_time"]),
                    last_edited_time=Timestamp.from_raw(
                        UTC, result_item["last_edited_time"]
                    ),
                )

            if not has_more:
                break

    def get_collection_item(self, item_id: NotionId) -> NotionCollectionItem:
        """Retrieve a particular item."""
        url = f"{NotionClientV2._API_ROOT}/pages/{item_id}"
        json_data = self._get(url)

        return NotionCollectionItem(
            notion_id=item_id,
            database_notion_id=NotionId.from_raw(json_data["parent"]["database_id"]),
            archived=json_data["archived"],
            properties=json_data["properties"],
            content_block=None,
            created_time=Timestamp.from_raw(UTC, json_data["created_time"]),
            last_edited_time=Timestamp.from_raw(UTC, json_data["last_edited_time"]),
        )

    def remove_collection_item(self, item_id: NotionId) -> None:
        """Archive a particular item, according to Notion rules."""
        url = f"{NotionClientV2._API_ROOT}/blocks/{item_id}"
        self._delete(url)

    def create_content_block(
        self, page_id: NotionId, block: NotionBlock
    ) -> NotionBlock:
        """Create a content block."""
        if block.notion_id != BAD_NOTION_ID:
            raise Exception("Trying to update a block which isn't created")
        url = f"{NotionClientV2._API_ROOT}/blocks/{page_id}/children"

        payload = {"children": [block.to_create_form()]}

        json_data = self._patch(url, payload)

        return block.assign_notion_id(NotionId.from_raw(json_data["id"]))

    def update_content_block(self, block: NotionBlock) -> NotionBlock:
        """Update a content block."""
        if block.notion_id == BAD_NOTION_ID:
            raise Exception("Trying to update a block which isn't created")
        url = f"{NotionClientV2._API_ROOT}/blocks/{block.notion_id}"
        payload = block.to_update_form()

        self._patch(url, payload)

        return block

    def remove_content_block(self, block_id: NotionId) -> None:
        """Remove a content block."""
        url = f"{NotionClientV2._API_ROOT}/blocks/{block_id}"
        self._delete(url)

    def _post(self, url: str, payload: Any) -> Any:  # type: ignore
        headers = {
            "Accept": "application/json",
            "Notion-Version": NotionClientV2._API_VERSION,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config.api_token}",
        }

        rate_limit_retry_idx = 0

        while rate_limit_retry_idx < self._MAX_RATE_LIMIT_RETRIES:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                return cast(JSONDictType, response.json())
            elif response.status_code == 404:
                raise NotionEntityNotFoundException()
            elif response.status_code == 429:
                # A rate-limiting occurs
                rate_limit_retry_idx += 1
                time.sleep(self._WAIT_TIME_BETWEEN_RATE_LIMIT_RETRIES_MS / 1000.0)
            else:
                print(url, str(payload))
                raise NotionClientException(
                    f"Notion API error code={response.status_code} message={response.text}"
                )

        raise NotionClientException("Unable to proceed past rate-limiting")

    def _patch(self, url: str, payload: Any) -> Any:  # type: ignore
        headers = {
            "Accept": "application/json",
            "Notion-Version": NotionClientV2._API_VERSION,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config.api_token}",
        }

        rate_limit_retry_idx = 0

        while rate_limit_retry_idx < self._MAX_RATE_LIMIT_RETRIES:
            response = requests.patch(url, json=payload, headers=headers)

            if response.status_code == 200:
                return cast(JSONDictType, response.json())
            elif response.status_code == 404:
                raise NotionEntityNotFoundException()
            elif response.status_code == 429:
                # A rate-limiting occurs
                rate_limit_retry_idx += 1
                time.sleep(self._WAIT_TIME_BETWEEN_RATE_LIMIT_RETRIES_MS / 1000.0)
            else:
                raise NotionClientException(
                    f"Notion API error code={response.status_code} message={response.text}"
                )

        raise NotionClientException("Unable to proceed past rate-limiting")

    def _get(self, url: str) -> Any:  # type: ignore
        headers = {
            "Accept": "application/json",
            "Notion-Version": NotionClientV2._API_VERSION,
            "Authorization": f"Bearer {self._config.api_token}",
        }

        rate_limit_retry_idx = 0

        while rate_limit_retry_idx < self._MAX_RATE_LIMIT_RETRIES:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return cast(JSONDictType, response.json())
            elif response.status_code == 404:
                raise NotionEntityNotFoundException()
            elif response.status_code == 429:
                # A rate-limiting occurs
                rate_limit_retry_idx += 1
                time.sleep(self._WAIT_TIME_BETWEEN_RATE_LIMIT_RETRIES_MS / 1000.0)
            else:
                raise NotionClientException(
                    f"Notion API error code={response.status_code} message={response.text}"
                )

        raise NotionClientException("Unable to proceed past rate-limiting")

    def _delete(self, url: str) -> None:
        headers = {
            "Accept": "application/json",
            "Notion-Version": NotionClientV2._API_VERSION,
            "Authorization": f"Bearer {self._config.api_token}",
        }

        rate_limit_retry_idx = 0

        while rate_limit_retry_idx < self._MAX_RATE_LIMIT_RETRIES:
            response = requests.delete(url, headers=headers)

            if response.status_code == 200:
                return
            elif response.status_code == 404:
                raise NotionEntityNotFoundException()
            elif response.status_code == 429:
                # A rate-limiting occurs
                rate_limit_retry_idx += 1
                time.sleep(self._WAIT_TIME_BETWEEN_RATE_LIMIT_RETRIES_MS / 1000.0)
            else:
                raise NotionClientException(
                    f"Notion API error code={response.status_code} message={response.text}"
                )

        raise NotionClientException("Unable to proceed past rate-limiting")
