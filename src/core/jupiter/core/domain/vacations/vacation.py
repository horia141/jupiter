"""A vacation."""
import typing

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction


@entity
class Vacation(LeafEntity):
    """A vacation."""

    vacation_collection: ParentLink
    name: VacationName
    start_date: ADate
    end_date: ADate

    @staticmethod
    @create_entity_action
    def new_vacation(
        ctx: DomainContext,
        vacation_collection_ref_id: EntityId,
        name: VacationName,
        start_date: ADate,
        end_date: ADate,
    ) -> "Vacation":
        """Create a vacation."""
        if start_date >= end_date:
            raise InputValidationError("Cannot set a start date after the end date")

        return Vacation._create(
            ctx,
            name=name,
            vacation_collection=ParentLink(vacation_collection_ref_id),
            start_date=start_date,
            end_date=end_date,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[VacationName],
        start_date: UpdateAction[ADate],
        end_date: UpdateAction[ADate],
    ) -> "Vacation":
        """Update a vacation's properties."""
        new_start_date = start_date.or_else(self.start_date)
        new_end_date = end_date.or_else(self.end_date)

        if new_start_date >= new_end_date:
            raise InputValidationError("Cannot set a start date after the end date")

        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            start_date=new_start_date,
            end_date=new_end_date,
        )

    def is_in_vacation(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this vacation."""
        vacation_start_date = self.start_date
        vacation_end_date = self.end_date
        return typing.cast(bool, vacation_start_date <= start_date) and typing.cast(
            bool,
            end_date <= vacation_end_date,
        )
