"""A calendar."""
from jupiter.core.domain.calendar.calendar_event import CalendarEvent
from jupiter.core.domain.calendar.calendar_name import CalendarName
from jupiter.core.domain.calendar.calendar_source import CalendarSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import BranchEntity, ContainsMany, IsRefId, ParentLink, TrunkEntity, create_entity_action, entity


@entity
class Calendar(BranchEntity):
    """A calendar."""
    
    calendar_collection: ParentLink

    source: CalendarSource
    name: CalendarName

    calendar_events = ContainsMany(CalendarEvent, calendar_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_calendar_for_user(
        ctx: DomainContext,
        calendar_collection_ref_id: EntityId,
        name: CalendarName,
    ) -> "Calendar":
        """Create a calendar."""
        return Calendar._create(
            ctx,
            calendar_collection=ParentLink(calendar_collection_ref_id),
            source=CalendarSource.USER,
            name=name,
        )
