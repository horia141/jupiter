"""A person on Notion-side."""
from dataclasses import dataclass
from typing import Optional, List

from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.prm.person import Person
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from framework.base.entity_id import EntityId
from framework.notion import NotionRow, BAD_NOTION_ID
from remote.notion.common import clean_eisenhower


@dataclass(frozen=True)
class NotionPerson(NotionRow[Person, None, 'NotionPerson.InverseExtraInfo']):
    """A person on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Inverse info."""
        project_ref_id: EntityId

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
    def new_notion_row(aggregate_root: Person, extra_info: None) -> 'NotionPerson':
        """Construct a new Notion row from a given aggregate root."""
        return NotionPerson(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            relationship=aggregate_root.relationship.for_notion(),
            catch_up_period=aggregate_root.catch_up_params.period.for_notion()
            if aggregate_root.catch_up_params else None,
            catch_up_eisen=[e.for_notion() for e in aggregate_root.catch_up_params.eisen]
            if aggregate_root.catch_up_params else None,
            catch_up_difficulty=aggregate_root.catch_up_params.difficulty.for_notion()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.difficulty else None,
            catch_up_actionable_from_day=aggregate_root.catch_up_params.actionable_from_day.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.actionable_from_day else None,
            catch_up_actionable_from_month=aggregate_root.catch_up_params.actionable_from_month.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.actionable_from_month else None,
            catch_up_due_at_time=str(aggregate_root.catch_up_params.due_at_time)
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.due_at_time else None,
            catch_up_due_at_day=aggregate_root.catch_up_params.due_at_day.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.due_at_day else None,
            catch_up_due_at_month=aggregate_root.catch_up_params.due_at_month.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.due_at_month else None,
            birthday=str(aggregate_root.birthday) if aggregate_root.birthday else None)

    def join_with_aggregate_root(self, aggregate_root: Person, extra_info: None) -> 'NotionPerson':
        """Construct a Notion row from a given aggregate root."""
        return NotionPerson(
            notion_id=self.notion_id,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            relationship=aggregate_root.relationship.for_notion(),
            catch_up_period=aggregate_root.catch_up_params.period.for_notion()
            if aggregate_root.catch_up_params else None,
            catch_up_eisen=[e.for_notion() for e in aggregate_root.catch_up_params.eisen]
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.eisen else [],
            catch_up_difficulty=aggregate_root.catch_up_params.difficulty.for_notion()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.difficulty else None,
            catch_up_actionable_from_day=aggregate_root.catch_up_params.actionable_from_day.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.actionable_from_day else None,
            catch_up_actionable_from_month=aggregate_root.catch_up_params.actionable_from_month.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.actionable_from_month else None,
            catch_up_due_at_time=str(aggregate_root.catch_up_params.due_at_time)
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.due_at_time else None,
            catch_up_due_at_day=aggregate_root.catch_up_params.due_at_day.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.due_at_day else None,
            catch_up_due_at_month=aggregate_root.catch_up_params.due_at_month.as_int()
            if aggregate_root.catch_up_params and aggregate_root.catch_up_params.due_at_month else None,
            birthday=str(aggregate_root.birthday) if aggregate_root.birthday else None)

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> Person:
        """Construct a new aggregate root from this notion row."""
        person_name = EntityName.from_raw(self.name)
        person_relationship = PersonRelationship.from_raw(self.relationship)
        person_catch_up_params = None
        if self.catch_up_period is not None:
            catch_up_period = RecurringTaskPeriod.from_raw(self.catch_up_period)
            person_catch_up_params = RecurringTaskGenParams(
                project_ref_id=extra_info.project_ref_id,
                period=catch_up_period,
                eisen=[Eisen.from_raw(e) for e in clean_eisenhower(self.catch_up_eisen)],
                difficulty=Difficulty.from_raw(self.catch_up_difficulty)
                if self.catch_up_difficulty else None,
                actionable_from_day=RecurringTaskDueAtDay.from_raw(catch_up_period, self.catch_up_actionable_from_day)
                if self.catch_up_actionable_from_day else None,
                actionable_from_month=RecurringTaskDueAtMonth.from_raw(catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_actionable_from_month else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.catch_up_due_at_time)
                if self.catch_up_due_at_time else None,
                due_at_day=RecurringTaskDueAtDay.from_raw(catch_up_period, self.catch_up_due_at_day)
                if self.catch_up_due_at_day else None,
                due_at_month=RecurringTaskDueAtMonth.from_raw(catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_due_at_month else None)
        person_birthday = PersonBirthday.from_raw(self.birthday) if self.birthday else None

        return Person.new_person(
            name=person_name,
            relationship=person_relationship,
            catch_up_params=person_catch_up_params,
            birthday=person_birthday,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: Person, extra_info: InverseExtraInfo) -> Person:
        """Obtain the aggregate root form of this, with a possible error."""
        person_name = EntityName.from_raw(self.name)
        person_relationship = PersonRelationship.from_raw(self.relationship)
        person_catch_up_params = None
        if self.catch_up_period is not None:
            catch_up_period = RecurringTaskPeriod.from_raw(self.catch_up_period)
            person_catch_up_params = RecurringTaskGenParams(
                project_ref_id=extra_info.project_ref_id,
                period=catch_up_period,
                eisen=[Eisen.from_raw(e) for e in
                       clean_eisenhower(self.catch_up_eisen)],
                difficulty=Difficulty.from_raw(
                    self.catch_up_difficulty) if self.catch_up_difficulty else None,
                actionable_from_day=RecurringTaskDueAtDay.from_raw(catch_up_period, self.catch_up_actionable_from_day)
                if self.catch_up_actionable_from_day else None,
                actionable_from_month=RecurringTaskDueAtMonth.from_raw(catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_actionable_from_month else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.catch_up_due_at_time)
                if self.catch_up_due_at_time else None,
                due_at_day=RecurringTaskDueAtDay.from_raw(catch_up_period, self.catch_up_due_at_day)
                if self.catch_up_due_at_day else None,
                due_at_month=RecurringTaskDueAtMonth.from_raw(catch_up_period, self.catch_up_due_at_month)
                if self.catch_up_due_at_month else None)
        person_birthday = PersonBirthday.from_raw(self.birthday) if self.birthday else None

        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_name(person_name, self.last_edited_time)
        aggregate_root.change_relationship(person_relationship, self.last_edited_time)
        aggregate_root.change_catch_up_params(person_catch_up_params, self.last_edited_time)
        aggregate_root.change_birthday(person_birthday, self.last_edited_time)

        return aggregate_root
