"""A person on Notion-side."""
from dataclasses import dataclass
from typing import Optional, List

from domain.prm.person import Person
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.shared import RecurringTaskGenParams
from models.basic import BasicValidator, EntityId
from models.framework import NotionRow, BAD_NOTION_ID
from remote.notion.common import clean_eisenhower


@dataclass()
class NotionPerson(NotionRow[Person, EntityId]):
    """A person on Notion-side."""

    name: str
    archived: bool
    relationship: Optional[str]
    catch_up_period: Optional[str]
    catch_up_eisen: Optional[List[str]]
    catch_up_difficulty: Optional[str]
    catch_up_actionable_from_day: Optional[int]
    catch_up_actionable_from_month: Optional[int]
    catch_up_due_at_time: Optional[str]
    catch_up_due_at_day: Optional[int]
    catch_up_due_at_month: Optional[int]
    birthday: Optional[str]

    @staticmethod
    def new_notion_row(aggregate_root: Person) -> 'NotionPerson':
        """Construct a new Notion row from a given aggregate root."""
        return NotionPerson(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            last_edited_time=aggregate_root.last_modified_time,
            name=aggregate_root.name,
            archived=aggregate_root.archived,
            relationship=aggregate_root.relationship.for_notion(),
            catch_up_period=aggregate_root.catch_up_params.period.for_notion()
            if aggregate_root.catch_up_params else None,
            catch_up_eisen=[e.for_notion() for e in aggregate_root.catch_up_params.eisen]
            if aggregate_root.catch_up_params else None,
            catch_up_difficulty=aggregate_root.catch_up_params.difficulty.for_notion()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.difficulty else None,
            catch_up_actionable_from_day=aggregate_root.catch_up_params.actionable_from_day
            if aggregate_root.catch_up_params else None,
            catch_up_actionable_from_month=aggregate_root.catch_up_params.actionable_from_month
            if aggregate_root.catch_up_params else None,
            catch_up_due_at_time=aggregate_root.catch_up_params.due_at_time
            if aggregate_root.catch_up_params else None,
            catch_up_due_at_day=aggregate_root.catch_up_params.due_at_day
            if aggregate_root.catch_up_params else None,
            catch_up_due_at_month=aggregate_root.catch_up_params.due_at_month
            if aggregate_root.catch_up_params else None,
            birthday=str(aggregate_root.birthday) if aggregate_root.birthday else None)

    def join_with_aggregate_root(self, aggregate_root: Person) -> 'NotionPerson':
        """Construct a Notion row from a given aggregate root."""
        return NotionPerson(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id,
            last_edited_time=aggregate_root.last_modified_time,
            name=aggregate_root.name,
            archived=aggregate_root.archived,
            relationship=aggregate_root.relationship.value,
            catch_up_period=aggregate_root.catch_up_params.period.for_notion()
            if aggregate_root.catch_up_params else None,
            catch_up_eisen=[e.for_notion() for e in aggregate_root.catch_up_params.eisen]
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.eisen else [],
            catch_up_difficulty=aggregate_root.catch_up_params.difficulty.for_notion()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.difficulty else None,
            catch_up_actionable_from_day=aggregate_root.catch_up_params.actionable_from_day
            if aggregate_root.catch_up_params else None,
            catch_up_actionable_from_month=aggregate_root.catch_up_params.actionable_from_month
            if aggregate_root.catch_up_params else None,
            catch_up_due_at_time=aggregate_root.catch_up_params.due_at_time if aggregate_root.catch_up_params else None,
            catch_up_due_at_day=aggregate_root.catch_up_params.due_at_day if aggregate_root.catch_up_params else None,
            catch_up_due_at_month=aggregate_root.catch_up_params.due_at_month
            if aggregate_root.catch_up_params else None,
            birthday=str(aggregate_root.birthday) if aggregate_root.birthday else None)

    def new_aggregate_root(self, extra_info: EntityId) -> Person:
        """Construct a new aggregate root from this notion row."""
        person_name = BasicValidator.entity_name_validate_and_clean(self.name)
        person_relationship = PersonRelationship.from_raw(self.relationship)
        person_catch_up_params = None
        if self.catch_up_period is not None:
            catch_up_period = BasicValidator.recurring_task_period_validate_and_clean(self.catch_up_period)
            person_catch_up_params = RecurringTaskGenParams(
                project_ref_id=extra_info,
                period=catch_up_period,
                eisen=[BasicValidator.eisen_validate_and_clean(e) for e in clean_eisenhower(self.catch_up_eisen)],
                difficulty=BasicValidator.difficulty_validate_and_clean(self.catch_up_difficulty)
                if self.catch_up_difficulty else None,
                actionable_from_day=BasicValidator.recurring_task_due_at_day_validate_and_clean(
                    catch_up_period, self.catch_up_actionable_from_day)
                if self.catch_up_actionable_from_day else None,
                actionable_from_month=BasicValidator.recurring_task_due_at_month_validate_and_clean(
                    catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_actionable_from_month else None,
                due_at_time=BasicValidator.recurring_task_due_at_time_validate_and_clean(self.catch_up_due_at_time)
                if self.catch_up_due_at_time else None,
                due_at_day=BasicValidator.recurring_task_due_at_day_validate_and_clean(
                    catch_up_period, self.catch_up_due_at_day)
                if self.catch_up_due_at_day else None,
                due_at_month=BasicValidator.recurring_task_due_at_month_validate_and_clean(
                    catch_up_period, self.catch_up_due_at_month) if self.catch_up_due_at_month else None)
        person_birthday = PersonBirthday.from_raw(self.birthday) if self.birthday else None

        return Person.new_person(
            name=person_name,
            relationship=person_relationship,
            catch_up_params=person_catch_up_params,
            birthday=person_birthday,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: Person, extra_info: EntityId) -> Person:
        """Obtain the aggregate root form of this, with a possible error."""
        person_name = BasicValidator.entity_name_validate_and_clean(self.name)
        person_relationship = PersonRelationship.from_raw(self.relationship)
        person_catch_up_params = None
        if self.catch_up_period is not None:
            catch_up_period = BasicValidator.recurring_task_period_validate_and_clean(self.catch_up_period)
            person_catch_up_params = RecurringTaskGenParams(
                project_ref_id=extra_info,
                period=catch_up_period,
                eisen=[BasicValidator.eisen_validate_and_clean(e) for e in
                       clean_eisenhower(self.catch_up_eisen)],
                difficulty=BasicValidator.difficulty_validate_and_clean(
                    self.catch_up_difficulty) if self.catch_up_difficulty else None,
                actionable_from_day=BasicValidator.recurring_task_due_at_day_validate_and_clean(
                    catch_up_period, self.catch_up_actionable_from_day)
                if self.catch_up_actionable_from_day else None,
                actionable_from_month=BasicValidator.recurring_task_due_at_month_validate_and_clean(
                    catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_actionable_from_month else None,
                due_at_time=BasicValidator.recurring_task_due_at_time_validate_and_clean(
                    self.catch_up_due_at_time) if self.catch_up_due_at_time else None,
                due_at_day=BasicValidator.recurring_task_due_at_day_validate_and_clean(
                    catch_up_period, self.catch_up_due_at_day)
                if self.catch_up_due_at_day else None,
                due_at_month=BasicValidator.recurring_task_due_at_month_validate_and_clean(
                    catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_due_at_month else None)
        person_birthday = PersonBirthday.from_raw(self.birthday) if self.birthday else None

        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_name(person_name, self.last_edited_time)
        aggregate_root.change_relationship(person_relationship, self.last_edited_time)
        aggregate_root.change_catch_up_params(person_catch_up_params, self.last_edited_time)
        aggregate_root.change_birthday(person_birthday, self.last_edited_time)

        return aggregate_root
