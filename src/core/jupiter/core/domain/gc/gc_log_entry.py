"""A particular entry in the GC log."""
from dataclasses import dataclass

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import (
    FIRST_VERSION,
    BranchEntity,
    Entity,
    LeafEntity,
)
from jupiter.core.framework.event import EventSource


@dataclass
class GCLogEntry(LeafEntity):
    """A particular entry in the GC log."""

    @dataclass
    class Opened(Entity.Created):
        """Event that gets triggered when a GC log entry is opened."""

    @dataclass
    class AddEntity(Entity.Updated):
        """Event that gets triggered when a GC log entry is opened."""

    @dataclass
    class Closed(Entity.Updated):
        """Event that gets triggered when a GC log entry is opened."""

    gc_log_ref_id: EntityId
    source: EventSource
    gc_targets: list[SyncTarget]
    opened: bool
    entity_records: list[EntitySummary]

    @staticmethod
    def new_log_entry(
        gc_log_ref_id: EntityId,
        gc_targets: list[SyncTarget],
        source: EventSource,
        created_time: Timestamp,
    ) -> "GCLogEntry":
        """Create a new GC log entry."""
        gc_log_entry = GCLogEntry(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                GCLogEntry.Opened.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=GCLogEntry.build_name(gc_targets, created_time),
            gc_log_ref_id=gc_log_ref_id,
            source=source,
            gc_targets=gc_targets,
            opened=True,
            entity_records=[],
        )
        return gc_log_entry

    @staticmethod
    def build_name(gc_targets: list[SyncTarget], created_time: Timestamp) -> EntityName:
        """Build the name for a GC log entry."""
        return EntityName(
            f"GC Log Entry for {','.join(str(g) for g in gc_targets)} at {created_time}"
        )

    def add_entity(
        self, entity: BranchEntity | LeafEntity, modification_time: Timestamp
    ) -> "GCLogEntry":
        """Add an entity to the GC log entry."""
        if not self.opened:
            raise Exception("Can't add an entity to a closed GC log entry.")
        return self._new_version(
            entity_records=[*self.entity_records, EntitySummary.from_entity(entity)],
            new_event=GCLogEntry.AddEntity.make_event_from_frame_args(
                self.source,
                self.version,
                modification_time,
            ),
        )

    def close(self, modification_time: Timestamp) -> "GCLogEntry":
        """Close the GC log entry."""
        return self._new_version(
            opened=False,
            new_event=GCLogEntry.Closed.make_event_from_frame_args(
                self.source,
                self.version,
                modification_time,
            ),
        )
