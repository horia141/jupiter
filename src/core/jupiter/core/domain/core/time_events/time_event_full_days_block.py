"""A full day block of time."""
import abc

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafSupportEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.repository import LeafEntityRepository


@entity
class TimeEventFullDaysBlock(LeafSupportEntity):
    """A full day block of time."""

    time_event_domain: ParentLink

    namespace: TimeEventNamespace
    source_entity_ref_id: EntityId
    start_date: ADate
    duration_days: int
    end_date: ADate

    @staticmethod
    @create_entity_action
    def new_time_event(
        ctx: DomainContext,
        time_event_domain_ref_id: EntityId,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        start_date: ADate,
        duration_days: int,
    ) -> "TimeEventFullDaysBlock":
        """Create a new time event."""
        if duration_days < 1:
            raise InputValidationError("Duration must be at least 1 day.")
        return TimeEventFullDaysBlock._create(
            ctx,
            name=NOT_USED_NAME,
            time_event_domain=ParentLink(time_event_domain_ref_id),
            namespace=namespace,
            source_entity_ref_id=source_entity_ref_id,
            start_date=start_date,
            duration_days=duration_days,
            end_date=start_date.add_days(duration_days),
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        start_date: ADate,
        duration_days: int,
    ) -> "TimeEventFullDaysBlock":
        """Update the time event."""
        if duration_days < 1:
            raise InputValidationError("Duration must be at least 1 day.")
        return self._new_version(
            ctx,
            start_date=start_date,
            duration_days=duration_days,
            end_date=start_date.add_days(duration_days),
        )


class TimeEventFullDaysBlockRepository(
    LeafEntityRepository[TimeEventFullDaysBlock], abc.ABC
):
    """A repository for time event full days blocks."""

    @abc.abstractmethod
    async def load_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
    ) -> TimeEventFullDaysBlock:
        """Load a time event full days block for a namespace and source entity."""

    @abc.abstractmethod
    async def find_all_between(
        self,
        parent_ref_id: EntityId,
        start_date: ADate,
        end_date: ADate,
    ) -> list[TimeEventFullDaysBlock]:
        """Find all time events in a range."""
