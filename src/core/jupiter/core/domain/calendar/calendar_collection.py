"""A collection of calendars."""
from jupiter.core.domain.calendar.calendar import Calendar
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import ContainsMany, IsRefId, ParentLink, TrunkEntity, create_entity_action, entity


@entity
class CalendarCollection(TrunkEntity):
    """A collection of calendars."""
    
    workspace: ParentLink

    calendars = ContainsMany(Calendar, calendar_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_calendar_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "CalendarCollection":
        """Create a calendar collection."""
        return CalendarCollection._create(ctx, workspace=ParentLink(workspace_ref_id))
    