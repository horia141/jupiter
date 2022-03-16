"""The SQLite based smart lists repository."""
from typing import Optional, Iterable, List, Final

from sqlalchemy import Table, Integer, Boolean, DateTime, ForeignKey, String, Column, MetaData, insert, update, \
    select, delete, JSON
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError

from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.smart_lists.infra.smart_list_collection_repository import SmartListCollectionRepository, \
    SmartListCollectionNotFoundError
from jupiter.domain.smart_lists.infra.smart_list_item_repository import SmartListItemRepository, \
    SmartListItemNotFoundError
from jupiter.domain.smart_lists.infra.smart_list_repository import SmartListRepository, SmartListAlreadyExistsError, \
    SmartListNotFoundError
from jupiter.domain.smart_lists.infra.smart_list_tag_repository import SmartListTagRepository, SmartListTagNotFoundError
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.url import URL
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import build_event_table, upsert_events, remove_events


class SqliteSmartListCollectionRepository(SmartListCollectionRepository):
    """The smart list collection repository."""

    _connection: Final[Connection]
    _smart_list_collection_table: Final[Table]
    _smart_list_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._smart_list_collection_table = Table(
            'smart_list_collection',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'workspace_ref_id', Integer, ForeignKey("workspace_ref_id.ref_id"),
                unique=True, index=True, nullable=False),
            keep_existing=True)
        self._smart_list_collection_event_table = build_event_table(self._smart_list_collection_table, metadata)

    def create(self, entity: SmartListCollection) -> SmartListCollection:
        """Create a smart list collection."""
        result = self._connection.execute(
            insert(self._smart_list_collection_table).values(
                ref_id=entity.ref_id.as_int() if entity.ref_id != BAD_REF_ID else None,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=
                entity.archived_time.to_db() if entity.archived_time else None,
                workspace_ref_id=entity.workspace_ref_id.as_int()))
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._smart_list_collection_event_table, entity)
        return entity

    def save(self, entity: SmartListCollection) -> SmartListCollection:
        """Save a big smart list collection."""
        result = self._connection.execute(
            update(self._smart_list_collection_table)
            .where(self._smart_list_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=
                entity.archived_time.to_db() if entity.archived_time else None,
                workspace_ref_id=entity.workspace_ref_id.as_int()))
        if result.rowcount == 0:
            raise SmartListCollectionNotFoundError("The smart list collection does not exist")
        upsert_events(self._connection, self._smart_list_collection_event_table, entity)
        return entity

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListCollection:
        """Load a smart list collection."""
        query_stmt = \
            select(self._smart_list_collection_table)\
                .where(self._smart_list_collection_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_collection_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListCollectionNotFoundError(f"Smart list collection with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_parent(self, parent_ref_id: EntityId) -> SmartListCollection:
        """Load a smart list collection for a given project."""
        query_stmt = \
            select(self._smart_list_collection_table)\
                .where(self._smart_list_collection_table.c.workspace_ref_id == parent_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListCollectionNotFoundError(
                f"Smart list collection for workspace {parent_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> SmartListCollection:
        return SmartListCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])))


class SqliteSmartListRepository(SmartListRepository):
    """A repository for lists."""

    _connection: Final[Connection]
    _smart_list_table: Final[Table]
    _smart_list_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._smart_list_table = Table(
            'smart_list',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('smart_list_collection_ref_id', Integer, ForeignKey('smart_list_collection.ref_id'), nullable=False),
            Column('the_key', String(32), nullable=False),
            Column('name', String(100), nullable=False),
            Column('icon', String(1), nullable=True),
            keep_existing=True)
        self._smart_list_event_table = build_event_table(self._smart_list_table, metadata)

    def create(self, entity: SmartList) -> SmartList:
        """Create a smart list."""
        try:
            result = self._connection.execute(
                insert(self._smart_list_table).values(
                    ref_id=entity.ref_id.as_int() if entity.ref_id != BAD_REF_ID else None,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db() if entity.archived_time else None,
                    smart_list_collection_ref_id=entity.smart_list_collection_ref_id.as_int(),
                    the_key=str(entity.key),
                    name=str(entity.name),
                    icon=entity.icon.to_safe() if entity.icon else None))
        except IntegrityError as err:
            raise SmartListAlreadyExistsError(f"Smart list with key {entity.key} already exists") from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._smart_list_event_table, entity)
        return entity

    def save(self, entity: SmartList) -> SmartList:
        """Save a smart list."""
        result = self._connection.execute(
            update(self._smart_list_table)
            .where(self._smart_list_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db() if entity.archived_time else None,
                smart_list_collection_ref_id=entity.smart_list_collection_ref_id.as_int(),
                the_key=str(entity.key),
                name=str(entity.name),
                icon=entity.icon.to_safe() if entity.icon else None))
        if result.rowcount == 0:
            raise SmartListNotFoundError("The smart list does not exist")
        upsert_events(self._connection, self._smart_list_event_table, entity)
        return entity

    def load_by_key(self, parent_ref_id: EntityId, key: SmartListKey) -> SmartList:
        """Load the smart list by key."""
        query_stmt = \
            select(self._smart_list_table)\
                .where(self._smart_list_table.c.smart_list_collection_ref_id == parent_ref_id.as_int())\
                .where(self._smart_list_table.c.the_key == str(key))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListNotFoundError(f"Smart list with key {key} does not exist")
        return self._row_to_entity(result)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartList:
        """Retrieve a smart list."""
        query_stmt = select(self._smart_list_table).where(self._smart_list_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListNotFoundError(f"Smart list with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> List[SmartList]:
        """Retrieve all smart lists."""
        query_stmt = \
            select(self._smart_list_table)\
            .where(self._smart_list_table.c.smart_list_collection_ref_id == parent_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._smart_list_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_keys:
            query_stmt = query_stmt.where(
                self._smart_list_table.c.the_key.in_(str(k) for k in filter_keys))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> SmartList:
        """Remove the smart list."""
        query_stmt = select(self._smart_list_table).where(self._smart_list_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListNotFoundError(f"Project with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._smart_list_table).where(self._smart_list_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._smart_list_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> SmartList:
        return SmartList(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            smart_list_collection_ref_id=EntityId.from_raw(str(row["smart_list_collection_ref_id"])),
            key=SmartListKey.from_raw(row["the_key"]),
            name=SmartListName.from_raw(row["name"]),
            icon=EntityIcon.from_safe(row["icon"]) if row["icon"] else None)


class SqliteSmartListTagRepository(SmartListTagRepository):
    """Sqlite based smart list tags repository."""

    _connection: Final[Connection]
    _smart_list_tag_table: Final[Table]
    _smart_list_tag_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._smart_list_tag_table = Table(
            'smart_list_tag',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('smart_list_ref_id', Integer, ForeignKey('smart_list.ref_id'), nullable=False),
            Column('tag_name', String(100), nullable=False),
            keep_existing=True)
        self._smart_list_tag_event_table = build_event_table(self._smart_list_tag_table, metadata)

    def create(self, entity: SmartListTag) -> SmartListTag:
        """Create a smart list tag."""
        result = self._connection.execute(
            insert(self._smart_list_tag_table).values(
                ref_id=entity.ref_id.as_int() if entity.ref_id != BAD_REF_ID else None,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db() if entity.archived_time else None,
                smart_list_ref_id=entity.smart_list_ref_id.as_int(),
                tag_name=str(entity.tag_name)))
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._smart_list_tag_event_table, entity)
        return entity

    def save(self, entity: SmartListTag) -> SmartListTag:
        """Save the smart list tag."""
        result = self._connection.execute(
            update(self._smart_list_tag_table)
            .where(self._smart_list_tag_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db() if entity.archived_time else None,
                smart_list_ref_id=entity.smart_list_ref_id.as_int(),
                tag_name=str(entity.tag_name)))
        if result.rowcount == 0:
            raise SmartListTagNotFoundError("The smart list tag does not exist")
        upsert_events(self._connection, self._smart_list_tag_event_table, entity)
        return entity

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListTag:
        """Retrieve the smart list."""
        query_stmt = select(self._smart_list_tag_table).where(self._smart_list_tag_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_tag_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListTagNotFoundError(f"The smart list tag with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[SmartListTag]:
        """Find all smart list tags."""
        return self.find_all_with_filters(
            parent_ref_id=parent_ref_id,
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids)

    def find_all_with_filters(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_tag_names: Optional[Iterable[SmartListTagName]] = None) -> List[SmartListTag]:
        """Find all smart list tags."""
        query_stmt = select(self._smart_list_tag_table) \
            .where(self._smart_list_tag_table.c.smart_list_ref_id == parent_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_tag_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._smart_list_tag_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_tag_names:
            query_stmt = query_stmt.where(self._smart_list_tag_table.c.tag_name.in_(str(fi) for fi in filter_tag_names))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> SmartListTag:
        """Remove a smart list tag."""
        query_stmt = select(self._smart_list_tag_table).where(self._smart_list_tag_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListTagNotFoundError(f"Smart list tag with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._smart_list_tag_table).where(self._smart_list_tag_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._smart_list_tag_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> SmartListTag:
        return SmartListTag(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            smart_list_ref_id=EntityId.from_raw(str(row["smart_list_ref_id"])),
            tag_name=SmartListTagName.from_raw(row["tag_name"]))


class SqliteSmartListItemRepository(SmartListItemRepository):
    """A repository for smart list items."""

    _connection: Final[Connection]
    _smart_list_item_table: Final[Table]
    _smart_list_item_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._smart_list_item_table = Table(
            'smart_list_item',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('smart_list_ref_id', Integer, ForeignKey('smart_list.ref_id'), nullable=False),
            Column('name', String(100), nullable=False),
            Column('is_done', Boolean, nullable=False),
            Column('tags_ref_id', JSON, nullable=False),
            Column('url', String, nullable=False),
            keep_existing=True)
        self._smart_list_item_event_table = build_event_table(self._smart_list_item_table, metadata)

    def create(self, entity: SmartListItem) -> SmartListItem:
        """Create a smart list item."""
        result = self._connection.execute(
            insert(self._smart_list_item_table).values(
                ref_id=entity.ref_id.as_int() if entity.ref_id != BAD_REF_ID else None,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db() if entity.archived_time else None,
                smart_list_ref_id=entity.smart_list_ref_id.as_int(),
                name=str(entity.name),
                is_done=entity.is_done,
                tags_ref_id=[ti.as_int() for ti in entity.tags_ref_id],
                url=str(entity.url) if entity.url else None))
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._smart_list_item_event_table, entity)
        return entity

    def save(self, entity: SmartListItem) -> SmartListItem:
        """Save the smart list item."""
        result = self._connection.execute(
            update(self._smart_list_item_table)
            .where(self._smart_list_item_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db() if entity.archived_time else None,
                smart_list_ref_id=entity.smart_list_ref_id.as_int(),
                name=str(entity.name),
                is_done=entity.is_done,
                tags_ref_id=[ti.as_int() for ti in entity.tags_ref_id],
                url=str(entity.url) if entity.url else None))
        if result.rowcount == 0:
            raise SmartListItemNotFoundError("The smart list item does not exist")
        upsert_events(self._connection, self._smart_list_item_event_table, entity)
        return entity

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListItem:
        """Load the smart list item."""
        query_stmt = select(self._smart_list_item_table).where(self._smart_list_item_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_item_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListItemNotFoundError(f"Smart list item with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[SmartListItem]:
        """Find all smart list items."""
        return self.find_all_with_filters(
            parent_ref_id=parent_ref_id,
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids)

    def find_all_with_filters(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_is_done: Optional[bool] = None,
            filter_tag_ref_ids: Optional[Iterable[EntityId]] = None) -> List[SmartListItem]:
        """Find all smart list items."""
        query_stmt = select(self._smart_list_item_table) \
            .where(self._smart_list_item_table.c.smart_list_ref_id == parent_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._smart_list_item_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = \
                query_stmt\
                .where(self._smart_list_item_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_is_done:
            query_stmt = query_stmt.where(self._smart_list_item_table.c.is_done.is_(filter_is_done))
        results = self._connection.execute(query_stmt)
        all_entities = [self._row_to_entity(row) for row in results]
        if filter_tag_ref_ids:
            # Can't do this in SQL that simply
            tag_set = frozenset(filter_tag_ref_ids)
            all_entities = [ent for ent in all_entities if len(tag_set.intersection(ent.tags_ref_id)) > 0]
        return all_entities

    def remove(self, ref_id: EntityId) -> SmartListItem:
        """Remove a smart list item."""
        query_stmt = select(self._smart_list_item_table).where(self._smart_list_item_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SmartListItemNotFoundError(f"Smart list item with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._smart_list_item_table).where(self._smart_list_item_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._smart_list_item_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> SmartListItem:
        return SmartListItem(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            smart_list_ref_id=EntityId.from_raw(str(row["smart_list_ref_id"])),
            name=SmartListItemName.from_raw(row["name"]),
            is_done=row["is_done"],
            tags_ref_id=[EntityId.from_raw(str(ti)) for ti in row["tags_ref_id"]],
            url=URL.from_raw(row["url"]) if row["url"] else None)
