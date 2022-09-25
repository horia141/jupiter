"""Common toolin for SQLite repositories."""

from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    String,
    JSON,
    delete,
    insert,
)
from sqlalchemy.engine import Connection

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.entity import Entity


def build_event_table(entity_table: Table, metadata: MetaData) -> Table:
    """Construct a standard events table for a given entity table."""
    return Table(
        entity_table.name + "_event",
        metadata,
        Column(
            "owner_ref_id", Integer, ForeignKey(entity_table.c.ref_id), primary_key=True
        ),
        Column("timestamp", DateTime, primary_key=True),
        Column("session_index", Integer, primary_key=True),
        Column("name", String(32), primary_key=True),
        Column("source", String(16), nullable=False),
        Column("owner_version", Integer, nullable=False),
        Column("kind", String(16), nullable=False),
        Column("data", JSON, nullable=False),
        keep_existing=True,
    )


def upsert_events(
    connection: Connection, event_table: Table, aggreggate_root: Entity
) -> None:
    """Upsert all the events for a given entity in an events table."""
    for event_idx, event in enumerate(aggreggate_root.events):
        connection.execute(
            insert(event_table)
            .prefix_with("OR IGNORE")
            .values(
                owner_ref_id=aggreggate_root.ref_id.as_int(),
                timestamp=event.timestamp.to_db(),
                session_index=event_idx,
                name=str(event.__class__.__name__),
                source=event.source.to_db(),
                owner_version=event.entity_version,
                kind=event.kind.to_db(),
                data=event.to_serializable_dict(),
            )
            # .on_conflict_do_nothing(
            #    index_elements=["owner_ref_id", "timestamp", "session_index", "name"]
            # )
        )


def remove_events(
    connection: Connection, event_table: Table, entity_ref_id: EntityId
) -> None:
    """Remove all the events for a given entity in an events table."""
    connection.execute(
        delete(event_table).where(event_table.c.owner_ref_id == entity_ref_id.as_int())
    )
