"""Common toolin for SQLite repositories."""
from sqlalchemy import Table, MetaData, Column, Integer, ForeignKey, DateTime, String, JSON
from sqlalchemy.dialects.sqlite import insert as sqliteInsert
from sqlalchemy.engine import Connection

from models.framework import AggregateRoot


def build_event_table(entity_table: Table, metadata: MetaData) -> Table:
    """Construct a standard events table for a given entity table."""
    return Table(
        entity_table.name + '_event',
        metadata,
        Column('owner_ref_id', Integer, ForeignKey(entity_table.c.ref_id), primary_key=True),
        Column('timestamp', DateTime, primary_key=True),
        Column('session_index', Integer, primary_key=True),
        Column('name', String(32), primary_key=True),
        Column('data', JSON, nullable=True),
        keep_existing=True)


def upsert_events(connection: Connection, event_table: Table, aggreggate_root: AggregateRoot) -> None:
    """Upsert all the events for a given entity in an events table."""
    for event_idx, event in enumerate(aggreggate_root.events):
        connection.execute(
            sqliteInsert(event_table)
            .values(
                owner_ref_id=int(aggreggate_root.ref_id),
                timestamp=event.timestamp,
                session_index=event_idx,
                name=str(event.__class__.__name__),
                data=event.to_serializable_dict())
            .on_conflict_do_nothing(index_elements=['owner_ref_id', 'timestamp', 'session_index', 'name']))
