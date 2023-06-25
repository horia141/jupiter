"""A person."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Person(LeafEntity):
    """A person."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Update(Entity.Updated):
        """Updated event."""

    person_collection_ref_id: EntityId
    name: PersonName
    relationship: PersonRelationship
    catch_up_params: Optional[RecurringTaskGenParams] = None
    birthday: Optional[PersonBirthday] = None

    @staticmethod
    def new_person(
        person_collection_ref_id: EntityId,
        name: PersonName,
        relationship: PersonRelationship,
        catch_up_params: Optional[RecurringTaskGenParams],
        birthday: Optional[PersonBirthday],
        source: EventSource,
        created_time: Timestamp,
    ) -> "Person":
        """Create a person."""
        person = Person(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Person.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            person_collection_ref_id=person_collection_ref_id,
            name=name,
            relationship=relationship,
            catch_up_params=catch_up_params,
            birthday=birthday,
        )
        return person

    def update(
        self,
        name: UpdateAction[PersonName],
        relationship: UpdateAction[PersonRelationship],
        catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]],
        birthday: UpdateAction[Optional[PersonBirthday]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Person":
        """Update info about the of the person."""
        return self._new_version(
            name=name.or_else(self.name),
            relationship=relationship.or_else(self.relationship),
            catch_up_params=catch_up_params.or_else(self.catch_up_params),
            birthday=birthday.or_else(self.birthday),
            new_event=Person.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def preparation_days_cnt_for_birthday(self) -> int:
        """How many days in advance to prepare for the birthday of this person."""
        if self.relationship == PersonRelationship.FAMILY:
            return 28
        elif self.relationship == PersonRelationship.FRIEND:
            return 14
        else:
            return 2

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.person_collection_ref_id
