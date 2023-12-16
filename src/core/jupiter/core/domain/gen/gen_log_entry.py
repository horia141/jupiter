"""A particular entry in the task generation log."""
from dataclasses import dataclass

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
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
class GenLogEntry(LeafEntity):
    """A particular entry in the task generation log."""

    @dataclass
    class Opened(Entity.Created):
        """Event that gets triggered when a task generation log entry is opened."""

    @dataclass
    class AddEntityCreated(Entity.Updated):
        """Event that gets triggered when an entity is added as created to the entry."""

    @dataclass
    class AddEntityUpdated(Entity.Updated):
        """Event that gets triggered when an entity is added as updated to the entry."""

    @dataclass
    class AddEntityRemoved(Entity.Updated):
        """Event that gets triggered when an entity is added as removed to the entry."""

    @dataclass
    class Closed(Entity.Updated):
        """Event that gets triggered when a task generation log entry is closed."""

    gen_log_ref_id: EntityId
    source: EventSource
    gen_even_if_not_modified: bool
    today: ADate
    gen_targets: list[SyncTarget]
    period: list[RecurringTaskPeriod] | None
    filter_project_ref_ids: list[EntityId] | None
    filter_habit_ref_ids: list[EntityId] | None
    filter_chore_ref_ids: list[EntityId] | None
    filter_metric_ref_ids: list[EntityId] | None
    filter_person_ref_ids: list[EntityId] | None
    filter_slack_task_ref_ids: list[EntityId] | None
    filter_email_task_ref_ids: list[EntityId] | None
    opened: bool
    entity_created_records: list[EntitySummary]
    entity_updated_records: list[EntitySummary]
    entity_removed_records: list[EntitySummary]

    @staticmethod
    def new_log_entry(
        gen_log_ref_id: EntityId,
        source: EventSource,
        gen_even_if_not_modified: bool,
        today: ADate,
        gen_targets: list[SyncTarget],
        period: list[RecurringTaskPeriod] | None,
        filter_project_ref_ids: list[EntityId] | None,
        filter_habit_ref_ids: list[EntityId] | None,
        filter_chore_ref_ids: list[EntityId] | None,
        filter_metric_ref_ids: list[EntityId] | None,
        filter_person_ref_ids: list[EntityId] | None,
        filter_slack_task_ref_ids: list[EntityId] | None,
        filter_email_task_ref_ids: list[EntityId] | None,
        created_time: Timestamp,
    ) -> "GenLogEntry":
        """Create a new task generation log entry."""
        gen_log_entry = GenLogEntry(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                GenLogEntry.Opened.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=GenLogEntry.build_name(gen_targets, created_time),
            gen_log_ref_id=gen_log_ref_id,
            source=source,
            gen_even_if_not_modified=gen_even_if_not_modified,
            today=today,
            gen_targets=gen_targets,
            period=period,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_habit_ref_ids=filter_habit_ref_ids,
            filter_chore_ref_ids=filter_chore_ref_ids,
            filter_metric_ref_ids=filter_metric_ref_ids,
            filter_person_ref_ids=filter_person_ref_ids,
            filter_slack_task_ref_ids=filter_slack_task_ref_ids,
            filter_email_task_ref_ids=filter_email_task_ref_ids,
            opened=True,
            entity_created_records=[],
            entity_updated_records=[],
            entity_removed_records=[],
        )
        return gen_log_entry

    @staticmethod
    def build_name(
        gen_targets: list[SyncTarget], created_time: Timestamp
    ) -> EntityName:
        """Build the name for a task generation log entry."""
        return EntityName(
            f"Task Generation Log Entry for {','.join(str(g) for g in gen_targets)} at {created_time}"
        )

    def add_entity_created(
        self, entity: BranchEntity | LeafEntity, modification_time: Timestamp
    ) -> "GenLogEntry":
        """Add an newly created entity to the task generation log entry."""
        if not self.opened:
            raise Exception(
                "Can't add an entity to a closed task generation log entry."
            )
        return self._new_version(
            entity_created_records=[
                *self.entity_created_records,
                EntitySummary.from_entity(entity),
            ],
            new_event=GenLogEntry.AddEntityCreated.make_event_from_frame_args(
                self.source,
                self.version,
                modification_time,
            ),
        )

    def add_entity_updated(
        self, entity: BranchEntity | LeafEntity, modification_time: Timestamp
    ) -> "GenLogEntry":
        """Add an updated entity to the task generation log entry."""
        if not self.opened:
            raise Exception(
                "Can't add an entity to a closed task generation log entry."
            )
        return self._new_version(
            entity_updated_records=[
                *self.entity_updated_records,
                EntitySummary.from_entity(entity),
            ],
            new_event=GenLogEntry.AddEntityUpdated.make_event_from_frame_args(
                self.source,
                self.version,
                modification_time,
            ),
        )

    def add_entity_removed(
        self, entity: BranchEntity | LeafEntity, modification_time: Timestamp
    ) -> "GenLogEntry":
        """Add an removed entity to the task generation log entry."""
        if not self.opened:
            raise Exception(
                "Can't add an entity to a closed task generation log entry."
            )
        return self._new_version(
            entity_removed_records=[
                *self.entity_removed_records,
                EntitySummary.from_entity(entity),
            ],
            new_event=GenLogEntry.AddEntityUpdated.make_event_from_frame_args(
                self.source,
                self.version,
                modification_time,
            ),
        )

    def close(self, modification_time: Timestamp) -> "GenLogEntry":
        """Close the task generation log entry."""
        return self._new_version(
            opened=False,
            new_event=GenLogEntry.Closed.make_event_from_frame_args(
                self.source,
                self.version,
                modification_time,
            ),
        )
