"""The centralised point for interacting with the Notion PRM database."""
import uuid
from typing import Iterable, ClassVar, cast, Dict, Final

from notion.collection import CollectionRowBlock

from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.notion_person import NotionPerson
from domain.prm.person_relationship import PersonRelationship
from models.basic import EntityId, BasicValidator, RecurringTaskPeriod, Eisen, Difficulty
from remote.notion.common import NotionPageLink, NotionId, NotionLockKey
from remote.notion.infra.client import NotionFieldProps, NotionFieldShow, NotionClient
from remote.notion.infra.collections_manager import CollectionsManager
from utils.storage import JSONDictType
from utils.time_provider import TimeProvider


class NotionPrmManager(PrmNotionManager):
    """The centralised point for interacting with the Notion PRM database."""

    _KEY: ClassVar[str] = "prm"
    _PAGE_NAME: ClassVar[str] = "PRM"

    _RELATIONSHIP: ClassVar[JSONDictType] = {
        "Family": {
            "name": PersonRelationship.FAMILY.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "Friend": {
            "name": PersonRelationship.FRIEND.for_notion(),
            "color": "blue",
            "in_board": True
        },
        "Acquaintance": {
            "name": PersonRelationship.ACQUAINTANCE.for_notion(),
            "color": "yellow",
            "in_board": True
        },
        "School Buddy": {
            "name": PersonRelationship.SCHOOL_BUDDY.for_notion(),
            "color": "red",
            "in_board": True
        },
        "Work Buddy": {
            "name": PersonRelationship.WORK_BUDDY.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "Colleague": {
            "name": PersonRelationship.COLLEAGUE.for_notion(),
            "color": "green",
            "in_board": True
        },
        "Other": {
            "name": PersonRelationship.OTHER.for_notion(),
            "color": "gray",
            "in_board": True
        }
    }

    _PERIOD: ClassVar[JSONDictType] = {
        "Daily": {
            "name": RecurringTaskPeriod.DAILY.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "Weekly": {
            "name": RecurringTaskPeriod.WEEKLY.for_notion(),
            "color": "green",
            "in_board": True
        },
        "Monthly": {
            "name": RecurringTaskPeriod.MONTHLY.for_notion(),
            "color": "yellow",
            "in_board": True
        },
        "Quarterly": {
            "name": RecurringTaskPeriod.QUARTERLY.for_notion(),
            "color": "blue",
            "in_board": True
        },
        "Yearly": {
            "name": RecurringTaskPeriod.YEARLY.for_notion(),
            "color": "red",
            "in_board": True
        }
    }

    _EISENHOWER: ClassVar[JSONDictType] = {
        "Urgent": {
            "name": Eisen.URGENT.for_notion(),
            "color": "red"
        },
        "Important": {
            "name": Eisen.IMPORTANT.for_notion(),
            "color": "blue"
        }
    }

    _DIFFICULTY = {
        "Easy": {
            "name": Difficulty.EASY.for_notion(),
            "color": "blue"
        },
        "Medium": {
            "name": Difficulty.MEDIUM.for_notion(),
            "color": "green"
        },
        "Hard": {
            "name": Difficulty.HARD.for_notion(),
            "color": "purple"
        }
    }

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "relationship": {
            "name": "Relationship",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _RELATIONSHIP.values()]
        },
        "catch-up-period": {
            "name": "Catch Up Period",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _PERIOD.values()]
        },
        "catch-up-eisen": {
            "name": "Catch Up Eisenhower",
            "type": "multi_select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _EISENHOWER.values()]
        },
        "catch-up-difficulty": {
            "name": "Catch Up Difficulty",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _DIFFICULTY.values()]
        },
        "catch-up-actionable-from-day": {
            "name": "Catch Up Actionable From Day",
            "type": "number",
        },
        "catch-up-actionable-from-month": {
            "name": "Catch Up Actionable From Month",
            "type": "number",
        },
        "catch-up-due-at-time": {
            "name": "Catch Up Due At Time",
            "type": "text",
        },
        "catch-up-due-at-day": {
            "name": "Catch Up Due At Day",
            "type": "number",
        },
        "catch-up-due-at-month": {
            "name": "Catch Up Due At Month",
            "type": "number",
        },
        "birthday": {
            "name": "Birthday",
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

    _SCHEMA_PROPERTIES = [
        NotionFieldProps(name="title", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="relationship", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="birthday", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="catch-up-period", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-eisen", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-difficulty", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-actionable-from-month", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-actionable-from-day", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-due-at-month", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-due-at-day", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="catch-up-due-at-time", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="archived", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="ref-id", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="last-edited-time", show=NotionFieldShow.SHOW)
    ]

    _DATABASE_VIEW_SCHEMA: JSONDictType = {
        "name": "Database",
        "type": "table",
        "format": {
            "table_properties": [{
                "width": 300,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "relationship",
                "visible": True
            }, {
                "width": 100,
                "property": "birthday",
                "visible": True
            }, {
                "width": 100,
                "property": "catch-up-period",
                "visible": True
            }, {
                "width": 100,
                "property": "catch-up-eisen",
                "visible": True
            }, {
                "width": 100,
                "property": "catch-up-difficulty",
                "visible": True
            }, {
                "width": 100,
                "property": "catch-up-actionable-from-day",
                "visible": False
            }, {
                "width": 100,
                "property": "catch-up-actionable-from-month",
                "visible": False
            }, {
                "width": 100,
                "property": "catch-up-due-at-time",
                "visible": False
            }, {
                "width": 100,
                "property": "catch-up-due-at-day",
                "visible": False
            }, {
                "width": 100,
                "property": "catch-up-due-at-month",
                "visible": False
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": True
            }]
        }
    }

    _time_provider: Final[TimeProvider]
    _basic_validator: Final[BasicValidator]
    _collections_manager: Final[CollectionsManager]

    def __init__(
            self, time_provider: TimeProvider, basic_validator: BasicValidator,
            collections_manager: CollectionsManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._basic_validator = basic_validator
        self._collections_manager = collections_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Upsert the root Notion structure."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(self._KEY),
            parent_page=parent_page,
            name=self._PAGE_NAME,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "database_view_id": self._DATABASE_VIEW_SCHEMA
            })

    def upsert_person(self, notion_person: NotionPerson) -> None:
        """Upsert a person on Notion-side."""
        self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{notion_person.ref_id}"),
            collection_key=NotionLockKey(self._KEY),
            new_row=notion_person,
            copy_row_to_notion_row=self.copy_row_to_notion_row)

    def save_person(self, notion_person: NotionPerson) -> None:
        """Save an already existing person on Notion-side."""
        self._collections_manager.save(
            key=NotionLockKey(f"{notion_person.ref_id}"),
            collection_key=NotionLockKey(self._KEY),
            row=notion_person,
            copy_row_to_notion_row=self.copy_row_to_notion_row)

    def remove_person(self, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""
        self._collections_manager.hard_remove(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(self._KEY))

    def load_person_by_ref_id(self, ref_id: EntityId) -> NotionPerson:
        """Retrieve a person from Notion-side."""
        return self._collections_manager.load(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(self._KEY),
            copy_notion_row_to_row=self.copy_notion_row_to_row)

    def load_all_persons(self) -> Iterable[NotionPerson]:
        """Retrieve all persons from Notion-side."""
        return self._collections_manager.load_all(
            collection_key=NotionLockKey(self._KEY),
            copy_notion_row_to_row=self.copy_notion_row_to_row)

    def load_all_saved_person_ref_ids(self) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""
        return self._collections_manager.load_all_saved_ref_ids(
            collection_key=NotionLockKey(self._KEY))

    def load_all_saved_person_notion_ids(self) -> Iterable[NotionId]:
        """Load ids of all persons we know about from Notion side."""
        return self._collections_manager.load_all_saved_notion_ids(
            collection_key=NotionLockKey(self._KEY))

    def drop_all_persons(self) -> None:
        """Drop all persons on Notion-side."""
        self._collections_manager.drop_all(
            collection_key=NotionLockKey(self._KEY))

    def link_local_and_notion_entries(self, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""
        self._collections_manager.quick_link_local_and_notion_entries(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(self._KEY),
            ref_id=ref_id,
            notion_id=notion_id)

    def copy_row_to_notion_row(
            self, client: NotionClient, row: NotionPerson, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.relationship = row.relationship
            notion_row.birthday = row.birthday
            notion_row.catch_up_period = row.catch_up_period
            notion_row.catch_up_eisenhower = row.catch_up_eisen
            notion_row.catch_up_difficulty = row.catch_up_difficulty
            notion_row.catch_up_actionable_from_day = row.catch_up_actionable_from_day
            notion_row.catch_up_actionable_from_month = row.catch_up_actionable_from_month
            notion_row.catch_up_due_at_time = row.catch_up_due_at_time
            notion_row.catch_up_due_at_day = row.catch_up_due_at_day
            notion_row.catch_up_due_at_month = row.catch_up_due_at_month
            notion_row.archived = row.archived
            notion_row.last_edited_time = self._basic_validator.timestamp_from_notion_timestamp(row.last_edited_time)
            notion_row.ref_id = row.ref_id

        return notion_row

    def copy_notion_row_to_row(self, notion_row: CollectionRowBlock) -> NotionPerson:
        """Transform the live system data to something suitable for basic storage."""
        return NotionPerson(
            notion_id=notion_row.id,
            name=notion_row.title,
            archived=notion_row.archived,
            relationship=notion_row.relationship,
            birthday=notion_row.birthday,
            catch_up_period=notion_row.catch_up_period,
            catch_up_eisen=notion_row.catch_up_eisenhower,
            catch_up_difficulty=notion_row.catch_up_difficulty,
            catch_up_actionable_from_day=notion_row.catch_up_actionable_from_day,
            catch_up_actionable_from_month=notion_row.catch_up_actionable_from_month,
            catch_up_due_at_time=notion_row.catch_up_due_at_time,
            catch_up_due_at_day=notion_row.catch_up_due_at_day,
            catch_up_due_at_month=notion_row.catch_up_due_at_month,
            last_edited_time=self._basic_validator.timestamp_from_notion_timestamp(notion_row.last_edited_time),
            ref_id=notion_row.ref_id)
