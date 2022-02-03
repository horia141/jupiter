"""A person."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.persons.person_name import PersonName
from jupiter.domain.persons.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Person(AggregateRoot):
    """A person."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Update(AggregateRoot.Updated):
        """Updated event."""

    person_collection_ref_id: EntityId
    name: PersonName
    relationship: PersonRelationship
    catch_up_params: Optional[RecurringTaskGenParams]
    birthday: Optional[PersonBirthday]

    @staticmethod
    def new_person(
            person_collection_ref_id: EntityId, name: PersonName, relationship: PersonRelationship,
            catch_up_params: Optional[RecurringTaskGenParams], birthday: Optional[PersonBirthday], source: EventSource,
            created_time: Timestamp) -> 'Person':
        """Create a person."""
        person = Person(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[Person.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            person_collection_ref_id=person_collection_ref_id,
            name=name,
            relationship=relationship,
            catch_up_params=catch_up_params,
            birthday=birthday)
        return person

    def update(
            self, name: UpdateAction[PersonName], relationship: UpdateAction[PersonRelationship],
            catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]],
            birthday: UpdateAction[Optional[PersonBirthday]], source: EventSource,
            modification_time: Timestamp) -> 'Person':
        """Change the name of the person."""
        return self._new_version(
            name=name.or_else(self.name),
            relationship=relationship.or_else(self.relationship),
            catch_up_params=catch_up_params.or_else(self.catch_up_params),
            birthday=birthday.or_else(self.birthday),
            new_event=Person.Update.make_event_from_frame_args(source, self.version, modification_time))

    @property
    def preparation_days_cnt_for_birthday(self) -> int:
        """How many days in advance to prepare for the birthday of this person."""
        if self.relationship == PersonRelationship.FAMILY:
            return 28
        elif self.relationship == PersonRelationship.FRIEND:
            return 14
        else:
            return 2
