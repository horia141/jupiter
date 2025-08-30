"""A particular entry in the stats log."""

import abc

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    CrownEntity,
    LeafSupportEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.repository import LeafEntityRepository


@entity
class StatsLogEntry(LeafSupportEntity):
    """A particular entry in the stats log."""

    stats_log: ParentLink
    source: EventSource
    stats_targets: list[SyncTarget]
    today: ADate
    filter_big_plan_ref_ids: list[EntityId] | None
    filter_journal_ref_ids: list[EntityId] | None
    filter_habit_ref_ids: list[EntityId] | None
    opened: bool
    entity_records: list[EntitySummary]

    @staticmethod
    @create_entity_action
    def new_log_entry(
        ctx: DomainContext,
        stats_log_ref_id: EntityId,
        stats_targets: list[SyncTarget],
        today: ADate,
        filter_big_plan_ref_ids: list[EntityId] | None = None,
        filter_journal_ref_ids: list[EntityId] | None = None,
        filter_habit_ref_ids: list[EntityId] | None = None,
    ) -> "StatsLogEntry":
        """Create a new stats log entry."""
        return StatsLogEntry._create(
            ctx,
            name=StatsLogEntry.build_name(stats_targets, today),
            stats_log=ParentLink(stats_log_ref_id),
            source=ctx.event_source,
            stats_targets=stats_targets,
            today=today,
            opened=True,
            filter_big_plan_ref_ids=filter_big_plan_ref_ids,
            filter_journal_ref_ids=filter_journal_ref_ids,
            filter_habit_ref_ids=filter_habit_ref_ids,
            entity_records=[],
        )

    @staticmethod
    def build_name(stats_targets: list[SyncTarget], today: ADate) -> EntityName:
        """Build the name for a stats log entry."""
        return EntityName(
            f"Stats Log Entry for {','.join(str(g) for g in stats_targets)} at {today}"
        )

    @update_entity_action
    def add_entity_updated(
        self,
        ctx: DomainContext,
        entity: CrownEntity,
    ) -> "StatsLogEntry":
        """Add an entity to the stats log entry."""
        if not self.opened:
            raise Exception("Can't add an entity to a closed stats log entry.")
        return self._new_version(
            ctx,
            entity_records=[*self.entity_records, EntitySummary.from_entity(entity)],
        )

    @update_entity_action
    def close(self, ctx: DomainContext) -> "StatsLogEntry":
        """Close the stats log entry."""
        return self._new_version(
            ctx,
            opened=False,
        )


class StatsLogEntryRepository(LeafEntityRepository[StatsLogEntry], abc.ABC):
    """A repository of stats log entries."""

    @abc.abstractmethod
    async def find_last(
        self,
        parent_ref_id: EntityId,
        limit: int,
    ) -> list[StatsLogEntry]:
        """Find the last N stats log entries."""
