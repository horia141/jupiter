"""A person on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.persons.person_name import PersonName
from jupiter.domain.persons.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionPerson(NotionLeafEntity[Person, None, None]):
    """A person on Notion-side."""

    name: str
    relationship: Optional[str]
    catch_up_period: Optional[str]
    catch_up_eisen: Optional[str]
    catch_up_difficulty: Optional[str]
    catch_up_actionable_from_day: Optional[int]
    catch_up_actionable_from_month: Optional[int]
    catch_up_due_at_time: Optional[str]
    catch_up_due_at_day: Optional[int]
    catch_up_due_at_month: Optional[int]
    birthday: Optional[str]

    @staticmethod
    def new_notion_entity(entity: Person, extra_info: None) -> "NotionPerson":
        """Construct a new Notion row from a given entity."""
        return NotionPerson(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            name=str(entity.name),
            archived=entity.archived,
            relationship=entity.relationship.for_notion(),
            catch_up_period=entity.catch_up_params.period.for_notion()
            if entity.catch_up_params
            else None,
            catch_up_eisen=entity.catch_up_params.eisen.for_notion()
            if entity.catch_up_params
            else None,
            catch_up_difficulty=entity.catch_up_params.difficulty.for_notion()
            if entity.catch_up_params and entity.catch_up_params.difficulty
            else None,
            catch_up_actionable_from_day=entity.catch_up_params.actionable_from_day.as_int()
            if entity.catch_up_params and entity.catch_up_params.actionable_from_day
            else None,
            catch_up_actionable_from_month=entity.catch_up_params.actionable_from_month.as_int()
            if entity.catch_up_params and entity.catch_up_params.actionable_from_month
            else None,
            catch_up_due_at_time=str(entity.catch_up_params.due_at_time)
            if entity.catch_up_params and entity.catch_up_params.due_at_time
            else None,
            catch_up_due_at_day=entity.catch_up_params.due_at_day.as_int()
            if entity.catch_up_params and entity.catch_up_params.due_at_day
            else None,
            catch_up_due_at_month=entity.catch_up_params.due_at_month.as_int()
            if entity.catch_up_params and entity.catch_up_params.due_at_month
            else None,
            birthday=str(entity.birthday) if entity.birthday else None,
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: None) -> Person:
        """Construct a new entity from this notion row."""
        person_name = PersonName.from_raw(self.name)
        person_relationship = PersonRelationship.from_raw(self.relationship)
        person_catch_up_params = None
        if self.catch_up_period is not None:
            catch_up_period = RecurringTaskPeriod.from_raw(self.catch_up_period)
            person_catch_up_params = RecurringTaskGenParams(
                period=catch_up_period,
                eisen=Eisen.from_raw(self.catch_up_eisen)
                if self.catch_up_eisen
                else Eisen.REGULAR,
                difficulty=Difficulty.from_raw(self.catch_up_difficulty)
                if self.catch_up_difficulty
                else None,
                actionable_from_day=RecurringTaskDueAtDay.from_raw(
                    catch_up_period, self.catch_up_actionable_from_day
                )
                if self.catch_up_actionable_from_day
                else None,
                actionable_from_month=RecurringTaskDueAtMonth.from_raw(
                    catch_up_period, self.catch_up_actionable_from_month
                )
                if self.catch_up_actionable_from_month
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.catch_up_due_at_time)
                if self.catch_up_due_at_time
                else None,
                due_at_day=RecurringTaskDueAtDay.from_raw(
                    catch_up_period, self.catch_up_due_at_day
                )
                if self.catch_up_due_at_day
                else None,
                due_at_month=RecurringTaskDueAtMonth.from_raw(
                    catch_up_period, self.catch_up_due_at_month
                )
                if self.catch_up_due_at_month
                else None,
            )
        person_birthday = (
            PersonBirthday.from_raw(self.birthday) if self.birthday else None
        )

        return Person.new_person(
            person_collection_ref_id=parent_ref_id,
            name=person_name,
            relationship=person_relationship,
            catch_up_params=person_catch_up_params,
            birthday=person_birthday,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: Person, extra_info: None
    ) -> NotionLeafApplyToEntityResult[Person]:
        """Obtain the entity form of this, with a possible error."""
        person_name = PersonName.from_raw(self.name)
        person_relationship = PersonRelationship.from_raw(self.relationship)
        person_catch_up_params = None
        if self.catch_up_period is not None:
            catch_up_period = RecurringTaskPeriod.from_raw(self.catch_up_period)
            person_catch_up_params = RecurringTaskGenParams(
                period=catch_up_period,
                eisen=Eisen.from_raw(self.catch_up_eisen)
                if self.catch_up_eisen
                else Eisen.REGULAR,
                difficulty=Difficulty.from_raw(self.catch_up_difficulty)
                if self.catch_up_difficulty
                else None,
                actionable_from_day=RecurringTaskDueAtDay.from_raw(
                    catch_up_period, self.catch_up_actionable_from_day
                )
                if self.catch_up_actionable_from_day
                else None,
                actionable_from_month=RecurringTaskDueAtMonth.from_raw(
                    catch_up_period, self.catch_up_due_at_month
                )
                if self.catch_up_actionable_from_month
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.catch_up_due_at_time)
                if self.catch_up_due_at_time
                else None,
                due_at_day=RecurringTaskDueAtDay.from_raw(
                    catch_up_period, self.catch_up_due_at_day
                )
                if self.catch_up_due_at_day
                else None,
                due_at_month=RecurringTaskDueAtMonth.from_raw(
                    catch_up_period, self.catch_up_due_at_month
                )
                if self.catch_up_due_at_month
                else None,
            )
        person_birthday = (
            PersonBirthday.from_raw(self.birthday) if self.birthday else None
        )

        return NotionLeafApplyToEntityResult.just(
            entity.update(
                name=UpdateAction.change_to(person_name),
                relationship=UpdateAction.change_to(person_relationship),
                catch_up_params=UpdateAction.change_to(person_catch_up_params),
                birthday=UpdateAction.change_to(person_birthday),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time,
            ).change_archived(
                archived=self.archived,
                source=EventSource.NOTION,
                archived_time=self.last_edited_time,
            )
        )

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        return self.name
