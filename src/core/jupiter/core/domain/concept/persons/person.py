"""A person."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.persons.person_birthday import PersonBirthday
from jupiter.core.domain.concept.persons.person_name import PersonName
from jupiter.core.domain.concept.persons.person_relationship import PersonRelationship
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class Person(LeafEntity):
    """A person."""

    person_collection: ParentLink
    name: PersonName
    relationship: PersonRelationship
    catch_up_params: RecurringTaskGenParams | None
    birthday: PersonBirthday | None

    note = OwnsAtMostOne(Note, domain=NoteDomain.PERSON, source_entity_ref_id=IsRefId())
    birthday_time_event_blocks = OwnsMany(
        TimeEventFullDaysBlock,
        namespace=TimeEventNamespace.PERSON_BIRTHDAY,
        source_entity_ref_id=IsRefId(),
    )
    catch_up_tasks = OwnsMany(
        InboxTask,
        source=InboxTaskSource.PERSON_CATCH_UP,
        source_entity_ref_id=IsRefId(),
    )
    birthday_tasks = OwnsMany(
        InboxTask,
        source=InboxTaskSource.PERSON_BIRTHDAY,
        source_entity_ref_id=IsRefId(),
    )

    @staticmethod
    @create_entity_action
    def new_person(
        ctx: DomainContext,
        person_collection_ref_id: EntityId,
        name: PersonName,
        relationship: PersonRelationship,
        catch_up_params: RecurringTaskGenParams | None,
        birthday: PersonBirthday | None,
    ) -> "Person":
        """Create a person."""
        return Person._create(
            ctx,
            person_collection=ParentLink(person_collection_ref_id),
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
        catch_up_params: UpdateAction[RecurringTaskGenParams | None],
        birthday: UpdateAction[PersonBirthday | None],
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

    def birthday_in_year(self, a_date: ADate) -> ADate:
        """Get the birthday of the person in the given year."""
        if self.birthday is None:
            raise Exception("This person has no birthday.")
        return self.birthday.birthday_in_year(a_date)
