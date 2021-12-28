"""A person."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.entity_name import EntityName
from jupiter.domain.prm.person_birthday import PersonBirthday
from jupiter.domain.prm.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.framework.aggregate_root import AggregateRoot
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp


@dataclass()
class Person(AggregateRoot):
    """A person."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class ChangeName(AggregateRoot.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class ChangeRelationship(AggregateRoot.Updated):
        """Change relationship event."""

    @dataclass(frozen=True)
    class ChangeCatchUpParams(AggregateRoot.Updated):
        """Change catch up params event."""

    @dataclass(frozen=True)
    class ChangeBirthday(AggregateRoot.Updated):
        """Change birthday event."""

    _name: EntityName
    _relationship: PersonRelationship
    _catch_up_params: Optional[RecurringTaskGenParams]
    _birthday: Optional[PersonBirthday]

    @staticmethod
    def new_person(
            name: EntityName, relationship: PersonRelationship, catch_up_params: Optional[RecurringTaskGenParams],
            birthday: Optional[PersonBirthday], created_time: Timestamp) -> 'Person':
        """Create a person."""
        person = Person(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _name=name,
            _relationship=relationship,
            _catch_up_params=catch_up_params,
            _birthday=birthday)
        person.record_event(Person.Created.make_event_from_frame_args(created_time))

        return person

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(Person.ChangeName.make_event_from_frame_args(modification_time))
        return self

    def change_relationship(self, relationship: PersonRelationship, modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        if self._relationship == relationship:
            return self
        self._relationship = relationship
        self.record_event(Person.ChangeRelationship.make_event_from_frame_args(modification_time))
        return self

    def change_catch_up_params(
            self, catch_up_params: Optional[RecurringTaskGenParams], modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        if self._catch_up_params == catch_up_params:
            return self
        self._catch_up_params = catch_up_params
        self.record_event(Person.ChangeCatchUpParams.make_event_from_frame_args(modification_time))
        return self

    def change_birthday(self, birthday: Optional[PersonBirthday], modification_time: Timestamp) -> 'Person':
        """Change the birthday of the person."""
        if self._birthday == birthday:
            return self
        self._birthday = birthday
        self.record_event(Person.ChangeBirthday.make_event_from_frame_args(modification_time))
        return self

    @property
    def preparation_days_cnt_for_birthday(self) -> int:
        """How many days in advance to prepare for the birthday of this person."""
        if self._relationship == PersonRelationship.FAMILY:
            return 28
        elif self._relationship == PersonRelationship.FRIEND:
            return 14
        else:
            return 2

    @property
    def name(self) -> EntityName:
        """The name of the person."""
        return self._name

    @property
    def relationship(self) -> PersonRelationship:
        """The relationship of the person."""
        return self._relationship

    @property
    def catch_up_params(self) -> Optional[RecurringTaskGenParams]:
        """The catch up params for this person."""
        return self._catch_up_params

    @property
    def birthday(self) -> Optional[PersonBirthday]:
        """The birthday of the person."""
        return self._birthday
