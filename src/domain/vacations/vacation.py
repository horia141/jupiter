"""A vacation."""
from dataclasses import dataclass, field

import typing

import pendulum
from pendulum import UTC

from models.basic import EntityName, ADate, Timestamp
from models.framework import AggregateRoot, Event, BAD_REF_ID, UpdateAction
from service.errors import ServiceValidationError


@dataclass()
class Vacation(AggregateRoot):
    """A vacation."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        name: EntityName
        start_date: ADate
        end_date: ADate

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)
        start_date: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)
        end_date: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)

    _name: EntityName
    _start_date: ADate
    _end_date: ADate

    @staticmethod
    def new_vacation(
            archived: bool, name: EntityName, start_date: ADate, end_date: ADate,
            created_time: Timestamp) -> 'Vacation':
        """Create a vacation."""
        if isinstance(start_date, pendulum.DateTime):
            raise ServiceValidationError(f"Vacation '{start_date}' should just start on a day")
        if isinstance(end_date, pendulum.DateTime):
            raise ServiceValidationError(f"Vacation '{end_date}' should just start on a day")
        if start_date >= end_date:
            raise ServiceValidationError("Cannot set a start date after the end date")

        vacation = Vacation(
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            _name=name,
            _start_date=start_date,
            _end_date=end_date)
        vacation.record_event(Vacation.Created(
            name=name, start_date=start_date, end_date=end_date, timestamp=created_time))

        return vacation

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Vacation':
        """Change the name of a metric."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(Vacation.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    def change_start_date(self, start_date: ADate, modification_time: Timestamp) -> 'Vacation':
        """Change the start date of a metric."""
        if self._start_date == start_date:
            return self
        if isinstance(start_date, pendulum.DateTime):
            raise ServiceValidationError(f"Vacation '{start_date}' should just start on a day")
        if start_date >= self._end_date:
            raise ServiceValidationError("Cannot set a start date after the end date")
        self._start_date = start_date
        self.record_event(Vacation.Updated(start_date=UpdateAction.change_to(start_date), timestamp=modification_time))
        return self

    def change_end_date(self, end_date: ADate, modification_time: Timestamp) -> 'Vacation':
        """Change the start date of a metric."""
        if self._end_date == end_date:
            return self
        if isinstance(end_date, pendulum.DateTime):
            raise ServiceValidationError(f"Vacation '{end_date}' should just start on a day")
        if end_date <= self._start_date:
            raise ServiceValidationError("Cannot set an end date before the start date")
        self._end_date = end_date
        self.record_event(Vacation.Updated(end_date=UpdateAction.change_to(end_date), timestamp=modification_time))
        return self

    def is_in_vacation(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this vacation."""
        if isinstance(start_date, pendulum.DateTime):
            vacation_start_date = pendulum.DateTime(
                self.start_date.year, self.start_date.month, self.start_date.day, tzinfo=UTC)
        else:
            vacation_start_date = self.start_date
        if isinstance(end_date, pendulum.DateTime):
            vacation_end_date = pendulum.DateTime(
                self.end_date.year, self.end_date.month, self.end_date.day, tzinfo=UTC).end_of("day")
        else:
            vacation_end_date = self.end_date
        return typing.cast(bool, vacation_start_date <= start_date) and \
               typing.cast(bool, end_date <= vacation_end_date)

    @property
    def name(self) -> EntityName:
        """The name of the vacation."""
        return self._name

    @property
    def start_date(self) -> ADate:
        """The start date of the vacation."""
        return self._start_date

    @property
    def end_date(self) -> ADate:
        """The end date of the vacation."""
        return self._end_date
