"""The SQLite based projects repository."""
import uuid
from typing import Final, Optional, Iterable

from sqlalchemy import insert, MetaData, Table, Column, Integer, Boolean, DateTime, String, ForeignKey, update, \
    select, delete
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError

from jupiter.domain.projects.infra.project_collection_repository import ProjectCollectionNotFoundError, \
    ProjectCollectionRepository
from jupiter.domain.projects.infra.project_repository import ProjectRepository, ProjectNotFoundError, \
    ProjectAlreadyExistsError
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import build_event_table, upsert_events, remove_events


class SqliteProjectCollectionRepository(ProjectCollectionRepository):
    """The project collection repository."""

    _connection: Final[Connection]
    _project_collection_table: Final[Table]
    _project_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._project_collection_table = Table(
            'project_collection',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'workspace_ref_id', Integer, ForeignKey("workspace.ref_id"), unique=True, index=True, nullable=False),
            keep_existing=True)
        self._project_collection_event_table = build_event_table(self._project_collection_table, metadata)

    def create(self, project_collection: ProjectCollection) -> ProjectCollection:
        """Create a project collection."""
        result = self._connection.execute(
            insert(self._project_collection_table).values(
                ref_id=project_collection.ref_id.as_int() if project_collection.ref_id != BAD_REF_ID else None,
                version=project_collection.version,
                archived=project_collection.archived,
                created_time=project_collection.created_time.to_db(),
                last_modified_time=project_collection.last_modified_time.to_db(),
                archived_time=project_collection.archived_time.to_db() if project_collection.archived_time else None,
                workspace_ref_id=project_collection.workspace_ref_id.as_int()))
        project_collection = project_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._project_collection_event_table, project_collection)
        return project_collection

    def save(self, project_collection: ProjectCollection) -> ProjectCollection:
        """Save a big project collection."""
        result = self._connection.execute(
            update(self._project_collection_table)
            .where(self._project_collection_table.c.ref_id == project_collection.ref_id.as_int())
            .values(
                version=project_collection.version,
                archived=project_collection.archived,
                created_time=project_collection.created_time.to_db(),
                last_modified_time=project_collection.last_modified_time.to_db(),
                archived_time=project_collection.archived_time.to_db() if project_collection.archived_time else None,
                workspace_ref_id=project_collection.workspace_ref_id.as_int()))
        if result.rowcount == 0:
            raise ProjectCollectionNotFoundError("The project collection does not exist")
        upsert_events(self._connection, self._project_collection_event_table, project_collection)
        return project_collection

    def load_by_workspace(self, workspace_ref_id: EntityId) -> ProjectCollection:
        """Load a project collection for a given project."""
        query_stmt = \
            select(self._project_collection_table)\
                .where(self._project_collection_table.c.workspace_ref_id == workspace_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ProjectCollectionNotFoundError(f"Big plan collection for project {workspace_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> ProjectCollection:
        return ProjectCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])))


class SqliteProjectRepository(ProjectRepository):
    """A repository for projects."""

    _connection: Final[Connection]
    _project_table: Final[Table]
    _project_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._project_table = Table(
            'project',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('project_collection_ref_id', Integer, ForeignKey('project_collection.ref_id'), nullable=False),
            Column('the_key', String(32), nullable=False),
            Column('name', String(100), nullable=False),
            Column('notion_link_uuid', String(16), nullable=False),
            keep_existing=True)
        self._project_event_table = build_event_table(self._project_table, metadata)

    def create(self, project: Project) -> Project:
        """Create a project."""
        try:
            result = self._connection.execute(
                insert(self._project_table).values(
                    ref_id=project.ref_id.as_int() if project.ref_id != BAD_REF_ID else None,
                    version=project.version,
                    archived=project.archived,
                    created_time=project.created_time.to_db(),
                    last_modified_time=project.last_modified_time.to_db(),
                    archived_time=project.archived_time.to_db() if project.archived_time else None,
                    project_collection_ref_id=project.project_collection_ref_id.as_int(),
                    the_key=str(project.key),
                    name=str(project.name),
                    notion_link_uuid=str(project.notion_link_uuid)))
        except IntegrityError as err:
            raise ProjectAlreadyExistsError(f"Project with key {project.key} already exists") from err
        project = project.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._project_event_table, project)
        return project

    def save(self, project: Project) -> Project:
        """Save a project."""
        result = self._connection.execute(
            update(self._project_table)
            .where(self._project_table.c.ref_id == project.ref_id.as_int())
            .values(
                version=project.version,
                archived=project.archived,
                created_time=project.created_time.to_db(),
                last_modified_time=project.last_modified_time.to_db(),
                archived_time=project.archived_time.to_db() if project.archived_time else None,
                project_collection_ref_id=project.project_collection_ref_id.as_int(),
                the_key=str(project.key),
                name=str(project.name),
                notion_link_uuid=str(project.notion_link_uuid)))
        if result.rowcount == 0:
            raise ProjectNotFoundError("The project does not exist")
        upsert_events(self._connection, self._project_event_table, project)
        return project

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Project:
        """Retrieve a project."""
        query_stmt = select(self._project_table).where(self._project_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._project_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ProjectNotFoundError(f"Project with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_key(self, project_collection_ref_id: EntityId, key: ProjectKey) -> Project:
        """Retrieve a project by its key."""
        query_stmt = \
            select(self._project_table)\
                .where(self._project_table.c.project_collection_ref_id == project_collection_ref_id.as_int())\
                .where(self._project_table.c.the_key == str(key))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ProjectNotFoundError(f"Project with key {key} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            project_collection_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Find all projects."""
        query_stmt = \
            select(self._project_table) \
            .where(self._project_table.c.project_collection_ref_id == project_collection_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._project_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = \
                query_stmt.where(self._project_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_keys:
            query_stmt = query_stmt.where(
                self._project_table.c.the_key.in_(str(k) for k in filter_keys))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> None:
        """Remove a project."""
        query_stmt = select(self._project_table).where(self._project_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ProjectNotFoundError(f"Project with id {ref_id} does not exist")
        remove_events(self._connection, self._project_event_table, ref_id)
        self._connection.execute(delete(self._project_table).where(self._project_table.c.ref_id == ref_id.as_int()))

    @staticmethod
    def _row_to_entity(row: Result) -> Project:
        return Project(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            project_collection_ref_id=EntityId.from_raw(str(row["project_collection_ref_id"])),
            key=ProjectKey.from_raw(row["the_key"]),
            name=ProjectName.from_raw(row["name"]),
            notion_link_uuid=uuid.UUID(row["notion_link_uuid"]))
