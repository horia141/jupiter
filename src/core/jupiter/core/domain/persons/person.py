"""A person."""
from typing import Optional

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsMany,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class Person(LeafEntity):
    """A person."""

    person_collection_ref_id: EntityId
    name: PersonName
    relationship: PersonRelationship
    catch_up_params: Optional[RecurringTaskGenParams] = None
    birthday: Optional[PersonBirthday] = None

    note = OwnsAtMostOne(Note, domain=NoteDomain.PERSON, source_entity_ref_id=IsRefId())
    catch_up_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.PERSON_CATCH_UP, person_ref_id=IsRefId()
    )
    birthday_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.PERSON_BIRTHDAY, person_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_person(
        ctx: DomainContext,
        person_collection_ref_id: EntityId,
        name: PersonName,
        relationship: PersonRelationship,
        catch_up_params: Optional[RecurringTaskGenParams],
        birthday: Optional[PersonBirthday],
    ) -> "Person":
        """Create a person."""
        return Person._create(
            ctx,
            person_collection_ref_id=person_collection_ref_id,
            name=name,
            relationship=relationship,
            catch_up_params=catch_up_params,
            birthday=birthday,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[PersonName],
        relationship: UpdateAction[PersonRelationship],
        catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]],
        birthday: UpdateAction[Optional[PersonBirthday]],
    ) -> "Person":
        """Update info about the of the person."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            relationship=relationship.or_else(self.relationship),
            catch_up_params=catch_up_params.or_else(self.catch_up_params),
            birthday=birthday.or_else(self.birthday),
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
