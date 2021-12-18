"""A person."""
from dataclasses import dataclass, field
from typing import Optional

from domain.entity_name import EntityName
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.timestamp import Timestamp
from models.framework import AggregateRoot, Event, UpdateAction, BAD_REF_ID


@dataclass()
class Person(AggregateRoot):
    """A person."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        name: EntityName
        relationship: PersonRelationship
        catch_up_params: Optional[RecurringTaskGenParams]
        birthday: Optional[PersonBirthday]

    @dataclass(frozen=True)
    class ChangeName(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)

    @dataclass(frozen=True)
    class ChangeRelationship(Event):
        """Change relationship event."""
        relationship: UpdateAction[PersonRelationship] = field(default_factory=UpdateAction.do_nothing)

    @dataclass(frozen=True)
    class ChangeCatchUpParams(Event):
        """Change catch up params event."""
        catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]] = field(default_factory=UpdateAction.do_nothing)

    @dataclass(frozen=True)
    class ChangeBirthday(Event):
        """Change birthday event."""
        birthday: UpdateAction[Optional[PersonBirthday]] = field(default_factory=UpdateAction.do_nothing)

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
        person.record_event(Person.Created(
            name=name, relationship=relationship, catch_up_params=catch_up_params, birthday=birthday,
            timestamp=created_time))

        return person

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(Person.ChangeName(
            name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    def change_relationship(self, relationship: PersonRelationship, modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        if self._relationship == relationship:
            return self
        self._relationship = relationship
        self.record_event(Person.ChangeRelationship(
            relationship=UpdateAction.change_to(relationship), timestamp=modification_time))
        return self

    def change_catch_up_params(
            self, catch_up_params: Optional[RecurringTaskGenParams], modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        if self._catch_up_params == catch_up_params:
            return self
        self._catch_up_params = catch_up_params
        self.record_event(Person.ChangeCatchUpParams(
            catch_up_params=UpdateAction.change_to(catch_up_params), timestamp=modification_time))
        return self

    def change_birthday(self, birthday: Optional[PersonBirthday], modification_time: Timestamp) -> 'Person':
        """Change the birthday of the person."""
        if self._birthday == birthday:
            return self
        self._birthday = birthday
        self.record_event(Person.ChangeBirthday(
            birthday=UpdateAction.change_to(birthday), timestamp=modification_time))
        return self

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
