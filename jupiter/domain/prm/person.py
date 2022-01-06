"""A person."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.prm.person_birthday import PersonBirthday
from jupiter.domain.prm.person_name import PersonName
from jupiter.domain.prm.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.update_action import UpdateAction


@dataclass()
class Person(AggregateRoot):
    """A person."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Update(AggregateRoot.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class ChangeCatchUpProject(AggregateRoot.Updated):
        """Change the catch up project."""

    name: PersonName
    relationship: PersonRelationship
    catch_up_params: Optional[RecurringTaskGenParams]
    birthday: Optional[PersonBirthday]

    @staticmethod
    def new_person(
            name: PersonName, relationship: PersonRelationship, catch_up_params: Optional[RecurringTaskGenParams],
            birthday: Optional[PersonBirthday], created_time: Timestamp) -> 'Person':
        """Create a person."""
        person = Person(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[],
            name=name,
            relationship=relationship,
            catch_up_params=catch_up_params,
            birthday=birthday)
        person.record_event(Person.Created.make_event_from_frame_args(created_time))

        return person

    def update(
            self, name: UpdateAction[PersonName], relationship: UpdateAction[PersonRelationship],
            catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]],
            birthday: UpdateAction[Optional[PersonBirthday]], modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        self.name = name.or_else(self.name)
        self.relationship = relationship.or_else(self.relationship)
        self.catch_up_params = catch_up_params.or_else(self.catch_up_params)
        self.birthday = birthday.or_else(self.birthday)
        self.record_event(Person.Update.make_event_from_frame_args(modification_time))
        return self

    def change_catch_up_project(self, catch_up_project_ref_id: EntityId, modification_time: Timestamp) -> 'Person':
        """Change the catch up project for a person."""
        if self.catch_up_params is None:
            raise InputValidationError("Cannot change the catch up project if there's no catch up to do")
        self.catch_up_params = self.catch_up_params.with_new_project_ref_id(catch_up_project_ref_id)
        self.record_event(Person.ChangeCatchUpProject.make_event_from_frame_args(modification_time))
        return self

    @property
    def preparation_days_cnt_for_birthday(self) -> int:
        """How many days in advance to prepare for the birthday of this person."""
        if self.relationship == PersonRelationship.FAMILY:
            return 28
        elif self.relationship == PersonRelationship.FRIEND:
            return 14
        else:
            return 2
