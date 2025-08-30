"""A particular entry in the task generation log."""

import abc

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
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
class GenLogEntry(LeafSupportEntity):
    """A particular entry in the task generation log."""

    gen_log: ParentLink
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
    @create_entity_action
    def new_log_entry(
        ctx: DomainContext,
        gen_log_ref_id: EntityId,
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
    ) -> "GenLogEntry":
        """Create a new task generation log entry."""
        return GenLogEntry._create(
            ctx,
            name=GenLogEntry.build_name(gen_targets, ctx.action_timestamp),
            gen_log=ParentLink(gen_log_ref_id),
            source=ctx.event_source,
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

    @staticmethod
    def build_name(
        gen_targets: list[SyncTarget], created_time: Timestamp
    ) -> EntityName:
        """Build the name for a task generation log entry."""
        return EntityName(
            f"Task Generation Log Entry for {','.join(str(g) for g in gen_targets)} at {created_time}"
        )

    @update_entity_action
    def add_entity_created(
        self, ctx: DomainContext, entity: CrownEntity
    ) -> "GenLogEntry":
        """Add an newly created entity to the task generation log entry."""
        if not self.opened:
            raise Exception(
                "Can't add an entity to a closed task generation log entry."
            )
        return self._new_version(
            ctx,
            entity_created_records=[
                *self.entity_created_records,
                EntitySummary.from_entity(entity),
            ],
        )

    @update_entity_action
    def add_entity_updated(
        self, ctx: DomainContext, entity: CrownEntity
    ) -> "GenLogEntry":
        """Add an updated entity to the task generation log entry."""
        if not self.opened:
            raise Exception(
                "Can't add an entity to a closed task generation log entry."
            )
        return self._new_version(
            ctx,
            entity_updated_records=[
                *self.entity_updated_records,
                EntitySummary.from_entity(entity),
            ],
        )

    @update_entity_action
    def add_entity_removed(
        self, ctx: DomainContext, entity: CrownEntity
    ) -> "GenLogEntry":
        """Add an removed entity to the task generation log entry."""
        if not self.opened:
            raise Exception(
                "Can't add an entity to a closed task generation log entry."
            )
        return self._new_version(
            ctx,
            entity_removed_records=[
                *self.entity_removed_records,
                EntitySummary.from_entity(entity),
            ],
        )

    @update_entity_action
    def close(self, ctx: DomainContext) -> "GenLogEntry":
        """Close the task generation log entry."""
        return self._new_version(
            ctx,
            opened=False,
        )


class GenLogEntryRepository(LeafEntityRepository[GenLogEntry], abc.ABC):
    """A repository of task generation log entries."""

    @abc.abstractmethod
    async def find_last(
        self,
        parent_ref_id: EntityId,
        limit: int,
    ) -> list[GenLogEntry]:
        """Find the last N task generation log entries."""
