"""Common toolin for SQLite repositories."""
from typing import cast

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import Entity
from jupiter.core.framework.event import Event
from jupiter.core.framework.realm import EventStoreRealm, RealmCodecRegistry, RealmThing
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.update_action import UpdateAction
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    delete,
    insert,
)
from sqlalchemy.ext.asyncio import AsyncConnection


def build_event_table(entity_table: Table, metadata: MetaData) -> Table:
    """Construct a standard events table for a given entity table."""
    return Table(
        entity_table.name + "_event",
        metadata,
        Column(
            "owner_ref_id",
            Integer,
            ForeignKey(entity_table.c.ref_id),
            primary_key=True,
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


async def upsert_events(
    realm_codec_registry: RealmCodecRegistry,
    connection: AsyncConnection,
    event_table: Table,
    aggreggate_root: Entity,
) -> None:
    """Upsert all the events for a given entity in an events table."""
    for event_idx, event in enumerate(aggreggate_root.events):
        await connection.execute(
            insert(event_table)
            .prefix_with("OR IGNORE")
            .values(
                owner_ref_id=aggreggate_root.ref_id.as_int(),
                timestamp=realm_codec_registry.db_encode(event.timestamp),
                session_index=event_idx,
                name=str(event.name),
                source=str(event.source.value),
                owner_version=event.entity_version,
                kind=str(event.kind.value),
                data=_serialize_event(realm_codec_registry, event),
            ),
            # .on_conflict_do_nothing(
            #    index_elements=["owner_ref_id", "timestamp", "session_index", "name"]
            # )
        )


def _serialize_event(
    realm_codec_registry: RealmCodecRegistry, event: Event
) -> RealmThing:
    """Transform an event into a serialisation-ready dictionary."""
    serialized_frame_args: dict[str, RealmThing] = {}
    for the_key, the_value in event.frame_args.items():
        # if not is_thing_ish_type(the_value.__class__):
        #     raise Exception(
        #         f"The domain should deal with things, but found {the_value.__class__}"
        #     )
        if isinstance(the_value, UpdateAction):
            if not the_value.should_change:
                serialized_frame_args[the_key] = {"should_change": False}
            else:
                serialized_frame_args[the_key] = {
                    "should_change": True,
                    "value": realm_codec_registry.db_encode(
                        cast(Thing, the_value.just_the_value), EventStoreRealm
                    ),
                }
        else:
            serialized_frame_args[the_key] = realm_codec_registry.db_encode(
                cast(Thing, the_value), EventStoreRealm
            )
    return serialized_frame_args


async def remove_events(
    connection: AsyncConnection,
    event_table: Table,
    entity_ref_id: EntityId,
) -> None:
    """Remove all the events for a given entity in an events table."""
    await connection.execute(
        delete(event_table).where(event_table.c.owner_ref_id == entity_ref_id.as_int()),
    )
