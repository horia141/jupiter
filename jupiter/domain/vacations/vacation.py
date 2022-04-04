"""A vacation."""
import typing
from dataclasses import dataclass

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.entity import Entity, FIRST_VERSION, LeafEntity
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Vacation(LeafEntity):
    """A vacation."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    vacation_collection_ref_id: EntityId
    name: VacationName
    start_date: ADate
    end_date: ADate

    @staticmethod
    def new_vacation(
        archived: bool,
        vacation_collection_ref_id: EntityId,
        name: VacationName,
        start_date: ADate,
        end_date: ADate,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Vacation":
        """Create a vacation."""
        if start_date >= end_date:
            raise InputValidationError("Cannot set a start date after the end date")

        vacation = Vacation(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[
                Vacation.Created.make_event_from_frame_args(
                    source, FIRST_VERSION, created_time
                )
            ],
            vacation_collection_ref_id=vacation_collection_ref_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

        return vacation

    def update(
        self,
        name: UpdateAction[VacationName],
        start_date: UpdateAction[ADate],
        end_date: UpdateAction[ADate],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Vacation":
        """Update a vacation's properties."""
        new_start_date = start_date.or_else(self.start_date)
        new_end_date = end_date.or_else(self.end_date)

        if new_start_date >= new_end_date:
            raise InputValidationError("Cannot set a start date after the end date")

        return self._new_version(
            name=name.or_else(self.name),
            start_date=new_start_date,
            end_date=new_end_date,
            new_event=Vacation.Updated.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    def is_in_vacation(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this vacation."""
        vacation_start_date = self.start_date.start_of_day()
        vacation_end_date = self.end_date.end_of_day()
        return typing.cast(bool, vacation_start_date <= start_date) and typing.cast(
            bool, end_date <= vacation_end_date
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.vacation_collection_ref_id
