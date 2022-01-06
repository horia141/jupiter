"""A vacation."""
import typing
from dataclasses import dataclass

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.aggregate_root import AggregateRoot
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.update_action import UpdateAction


@dataclass()
class Vacation(AggregateRoot):
    """A vacation."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    name: VacationName
    start_date: ADate
    end_date: ADate

    @staticmethod
    def new_vacation(
            archived: bool, name: VacationName, start_date: ADate, end_date: ADate,
            created_time: Timestamp) -> 'Vacation':
        """Create a vacation."""
        if start_date >= end_date:
            raise InputValidationError("Cannot set a start date after the end date")

        vacation = Vacation(
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            name=name,
            start_date=start_date,
            end_date=end_date)
        vacation.record_event(Vacation.Created.make_event_from_frame_args(created_time))

        return vacation

    def update(
            self, name: UpdateAction[VacationName], start_date: UpdateAction[ADate], end_date: UpdateAction[ADate],
            modification_time: Timestamp) -> 'Vacation':
        """Update a vacation's properties."""
        new_start_date = start_date.or_else(self.start_date)
        new_end_date = end_date.or_else(self.end_date)

        if new_start_date >= new_end_date:
            raise InputValidationError("Cannot set a start date after the end date")
        self.name = name.or_else(self.name)
        self.start_date = new_start_date
        self.end_date = new_end_date
        self.record_event(Vacation.Updated.make_event_from_frame_args(modification_time))
        return self

    def is_in_vacation(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this vacation."""
        vacation_start_date = self.start_date.start_of_day()
        vacation_end_date = self.end_date.end_of_day()
        return typing.cast(bool, vacation_start_date <= start_date) and \
               typing.cast(bool, end_date <= vacation_end_date)
