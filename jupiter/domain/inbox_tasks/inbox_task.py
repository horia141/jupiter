"""An inbox task."""
from dataclasses import dataclass
from typing import Optional, Type

import pendulum
from pendulum import UTC

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


class CannotModifyGeneratedTaskError(Exception):
    """Exception raised when you're trying to modify a generated task."""

    field: str

    def __init__(self, field: str) -> None:
        """Constructor."""
        super().__init__(f"Cannot modify generated inbox task field {field}")
        self.field = field


@dataclass(frozen=True)
class InboxTask(AggregateRoot):
    """An inbox task."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class GeneratedForHabit(AggregateRoot.Created):
        """Generated for a habit event."""

    @dataclass(frozen=True)
    class GeneratedForChore(AggregateRoot.Created):
        """Generated for a chore event."""

    @dataclass(frozen=True)
    class GeneratedForMetricCollection(AggregateRoot.Created):
        """Generated for metric collection event."""

    @dataclass(frozen=True)
    class GeneratedForPersonCatchUp(AggregateRoot.Created):
        """Generated for person catch up event."""

    @dataclass(frozen=True)
    class GeneratedForPersonBirthday(AggregateRoot.Created):
        """Generated for person birthday event."""

    @dataclass(frozen=True)
    class ChangeProject(AggregateRoot.Updated):
        """Changed the project event."""

    @dataclass(frozen=True)
    class AssociatedWithBigPlan(AggregateRoot.Updated):
        """Associated with big plan event."""

    @dataclass(frozen=True)
    class ReleaseFromBigPlan(AggregateRoot.Updated):
        """Release from big plan event."""

    @dataclass(frozen=True)
    class UpdatedLinkToBigPlan(AggregateRoot.Updated):
        """Updated link to big plan event."""

    @dataclass(frozen=True)
    class UpdatedLinkToHabit(AggregateRoot.Updated):
        """Updated link to habit event."""

    @dataclass(frozen=True)
    class UpdatedLinkToChore(AggregateRoot.Updated):
        """Updated link to chore event."""

    @dataclass(frozen=True)
    class UpdatedLinkToMetricCollection(AggregateRoot.Updated):
        """Updated link to recurring task event."""

    @dataclass(frozen=True)
    class UpdatedLinkToPersonCatchUp(AggregateRoot.Updated):
        """Updated link to a person catch up task event."""

    @dataclass(frozen=True)
    class UpdatedLinkToPersonBirthday(AggregateRoot.Updated):
        """Updated link to a person birthday task event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class UpdatedGenerated(AggregateRoot.Updated):
        """Updated event."""

    inbox_task_collection_ref_id: EntityId
    source: InboxTaskSource
    project_ref_id: EntityId
    big_plan_ref_id: Optional[EntityId]
    habit_ref_id: Optional[EntityId]
    chore_ref_id: Optional[EntityId]
    metric_ref_id: Optional[EntityId]
    person_ref_id: Optional[EntityId]
    name: InboxTaskName
    status: InboxTaskStatus
    eisen: Eisen
    difficulty: Optional[Difficulty]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    recurring_timeline: Optional[str]
    recurring_gen_right_now: Optional[Timestamp]  # Time for which this inbox task was generated
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]

    @staticmethod
    def new_inbox_task(
            inbox_task_collection_ref_id: EntityId, archived: bool, name: InboxTaskName,
            status: InboxTaskStatus, project_ref_id: EntityId, big_plan: Optional[BigPlan], eisen: Optional[Eisen],
            difficulty: Optional[Difficulty], actionable_date: Optional[ADate], due_date: Optional[ADate],
            source: EventSource, created_time: Timestamp) -> 'InboxTask':
        """Created an inbox task."""
        InboxTask._check_actionable_and_due_dates(actionable_date, due_date)

        inbox_task = InboxTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[InboxTask.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            source=InboxTaskSource.USER if big_plan is None else InboxTaskSource.BIG_PLAN,
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan.ref_id if big_plan else None,
            habit_ref_id=None,
            chore_ref_id=None,
            metric_ref_id=None,
            person_ref_id=None,
            name=name,
            status=status,
            eisen=eisen if eisen else Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date or (big_plan.actionable_date if big_plan else None),
            due_date=due_date or (big_plan.due_date if big_plan else None),
            recurring_timeline=None,
            recurring_gen_right_now=None,
            accepted_time=created_time if status.is_accepted_or_more else None,
            working_time=created_time if status.is_working_or_more else None,
            completed_time=created_time if status.is_completed else None)
        return inbox_task

    @staticmethod
    def new_inbox_task_for_habit(
            inbox_task_collection_ref_id: EntityId, name: InboxTaskName, project_ref_id: EntityId,
            habit_ref_id: EntityId, recurring_task_timeline: str, recurring_task_gen_right_now: Timestamp,
            eisen: Eisen, difficulty: Optional[Difficulty], actionable_date: Optional[ADate],
            due_date: Optional[ADate], source: EventSource, created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[InboxTask.GeneratedForHabit.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            source=InboxTaskSource.HABIT,
            project_ref_id=project_ref_id,
            big_plan_ref_id=None,
            habit_ref_id=habit_ref_id,
            chore_ref_id=None,
            metric_ref_id=None,
            person_ref_id=None,
            name=name,
            status=InboxTaskStatus.RECURRING,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_timeline=recurring_task_timeline,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=created_time,
            working_time=None,
            completed_time=None)
        return inbox_task

    @staticmethod
    def new_inbox_task_for_chore(
            inbox_task_collection_ref_id: EntityId, name: InboxTaskName, project_ref_id: EntityId,
            chore_ref_id: EntityId, recurring_task_timeline: str, recurring_task_gen_right_now: Timestamp,
            eisen: Eisen, difficulty: Optional[Difficulty], actionable_date: Optional[ADate],
            due_date: Optional[ADate], source: EventSource, created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[InboxTask.GeneratedForChore.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            source=InboxTaskSource.CHORE,
            project_ref_id=project_ref_id,
            big_plan_ref_id=None,
            habit_ref_id=None,
            chore_ref_id=chore_ref_id,
            metric_ref_id=None,
            person_ref_id=None,
            name=name,
            status=InboxTaskStatus.RECURRING,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_timeline=recurring_task_timeline,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=created_time,
            working_time=None,
            completed_time=None)
        return inbox_task

    @staticmethod
    def new_inbox_task_for_metric_collection(
            inbox_task_collection_ref_id: EntityId, name: InboxTaskName, project_ref_id: EntityId,
            metric_ref_id: EntityId, recurring_task_timeline: str, recurring_task_gen_right_now: Timestamp,
            eisen: Eisen, difficulty: Optional[Difficulty], actionable_date: Optional[ADate], due_date: Optional[ADate],
            source: EventSource, created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                InboxTask.GeneratedForMetricCollection.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            source=InboxTaskSource.METRIC,
            project_ref_id=project_ref_id,
            big_plan_ref_id=None,
            habit_ref_id=None,
            chore_ref_id=None,
            metric_ref_id=metric_ref_id,
            person_ref_id=None,
            name=InboxTask._build_name_for_collection_task(name),
            status=InboxTaskStatus.RECURRING,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_timeline=recurring_task_timeline,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=created_time,
            working_time=None,
            completed_time=None)
        return inbox_task

    @staticmethod
    def new_inbox_task_for_person_catch_up(
            inbox_task_collection_ref_id: EntityId, name: InboxTaskName, project_ref_id: EntityId,
            person_ref_id: EntityId, recurring_task_timeline: str, eisen: Eisen, difficulty: Optional[Difficulty],
            recurring_task_gen_right_now: Timestamp, actionable_date: Optional[ADate],
            due_date: Optional[ADate], source: EventSource, created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                InboxTask.GeneratedForPersonCatchUp.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            source=InboxTaskSource.PERSON_CATCH_UP,
            project_ref_id=project_ref_id,
            big_plan_ref_id=None,
            habit_ref_id=None,
            chore_ref_id=None,
            metric_ref_id=None,
            person_ref_id=person_ref_id,
            name=InboxTask._build_name_for_catch_up_task(name),
            status=InboxTaskStatus.RECURRING,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_timeline=recurring_task_timeline,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=created_time,
            working_time=None,
            completed_time=None)
        return inbox_task

    @staticmethod
    def new_inbox_task_for_person_birthday(
            inbox_task_collection_ref_id: EntityId, name: InboxTaskName, project_ref_id: EntityId,
            person_ref_id: EntityId, recurring_task_timeline: str, recurring_task_gen_right_now: Timestamp,
            preparation_days_cnt: int, due_date: ADate, source: EventSource, created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                InboxTask.GeneratedForPersonBirthday.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            source=InboxTaskSource.PERSON_BIRTHDAY,
            project_ref_id=project_ref_id,
            big_plan_ref_id=None,
            habit_ref_id=None,
            chore_ref_id=None,
            metric_ref_id=None,
            person_ref_id=person_ref_id,
            name=InboxTask._build_name_for_birthday_task(name),
            status=InboxTaskStatus.RECURRING,
            eisen=Eisen.IMPORTANT,
            difficulty=Difficulty.EASY,
            actionable_date=due_date.subtract_days(preparation_days_cnt),
            due_date=due_date,
            recurring_timeline=recurring_task_timeline,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=created_time,
            working_time=None,
            completed_time=None)
        return inbox_task

    def change_project(
            self, project_ref_id: EntityId, source: EventSource, modification_time: Timestamp) -> 'InboxTask':
        """Change the project for the inbox task."""
        if not self.source.allow_user_changes:
            raise CannotModifyGeneratedTaskError("project")
        return self._new_version(
            project_ref_id=project_ref_id,
            new_event=InboxTask.ChangeProject.make_event_from_frame_args(source, self.version, modification_time))

    def associate_with_big_plan(
            self, project_ref_id: EntityId, big_plan_ref_id: EntityId, _big_plan_name: BigPlanName,
            source: EventSource, modification_time: Timestamp) -> 'InboxTask':
        """Associate an inbox task with a big plan."""
        if not self.source.allow_user_changes:
            raise CannotModifyGeneratedTaskError("big plan")

        return self._new_version(
            source=InboxTaskSource.BIG_PLAN,
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            new_event=
            InboxTask.AssociatedWithBigPlan.make_event_from_frame_args(source, self.version, modification_time))

    def release_from_big_plan(
            self, source: EventSource, modification_time: Timestamp) -> 'InboxTask':
        """Release an inbox task from a big plan."""
        if not self.source.allow_user_changes:
            raise CannotModifyGeneratedTaskError("big plan")

        return self._new_version(
            source=InboxTaskSource.USER,
            big_plan_ref_id=None,
            new_event=
            InboxTask.ReleaseFromBigPlan.make_event_from_frame_args(source, self.version, modification_time))

    def update_link_to_big_plan(
            self, project_ref_id: EntityId, big_plan_ref_id: EntityId, source: EventSource,
            modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a big plan."""
        if self.source is not InboxTaskSource.BIG_PLAN:
            raise InputValidationError(f"Cannot reassociate a task which isn't a big plan one '{self.name}'")
        if self.big_plan_ref_id != big_plan_ref_id:
            raise InputValidationError(f"Cannot reassociate a task which is not with the big plan '{self.name}'")

        return self._new_version(
            project_ref_id=project_ref_id,
            new_event=
            InboxTask.UpdatedLinkToBigPlan.make_event_from_frame_args(source, self.version, modification_time))

    def update_link_to_habit(
            self, project_ref_id: EntityId, name: InboxTaskName, timeline: str, actionable_date: Optional[ADate],
            due_date: ADate, eisen: Eisen, difficulty: Optional[Difficulty], source: EventSource,
            modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a habit."""
        if self.source is not InboxTaskSource.HABIT:
            raise Exception(f"Cannot associate a task which is not a habit for '{self.name}'")
        return self._new_version(
            project_ref_id=project_ref_id,
            name=name,
            actionable_date=actionable_date,
            due_date=due_date,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=timeline,
            new_event=InboxTask.UpdatedLinkToHabit.make_event_from_frame_args(source, self.version, modification_time))

    def update_link_to_chore(
            self, project_ref_id: EntityId, name: InboxTaskName, timeline: str, actionable_date: Optional[ADate],
            due_date: ADate, eisen: Eisen, difficulty: Optional[Difficulty], source: EventSource,
            modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a chore."""
        if self.source is not InboxTaskSource.CHORE:
            raise Exception(f"Cannot associate a task which is not a chore for '{self.name}'")
        return self._new_version(
            project_ref_id=project_ref_id,
            name=name,
            actionable_date=actionable_date,
            due_date=due_date,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=timeline,
            new_event=InboxTask.UpdatedLinkToChore.make_event_from_frame_args(source, self.version, modification_time))

    def update_link_to_metric(
            self, project_ref_id: EntityId, name: InboxTaskName, recurring_timeline: str, eisen: Eisen,
            difficulty: Optional[Difficulty], actionable_date: Optional[ADate], due_time: ADate, source: EventSource,
            modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a metric."""
        if self.source is not InboxTaskSource.METRIC:
            raise Exception(
                f"Cannot associate a task which is not recurring with a recurring one '{self.name}'")
        return self._new_version(
            project_ref_id=project_ref_id,
            name=self._build_name_for_collection_task(name),
            actionable_date=actionable_date,
            due_date=due_time,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=recurring_timeline,
            new_event=
            InboxTask.UpdatedLinkToMetricCollection.make_event_from_frame_args(source, self.version, modification_time))

    def update_link_to_person_catch_up(
            self, project_ref_id: EntityId, name: InboxTaskName, recurring_timeline: str, eisen: Eisen,
            difficulty: Optional[Difficulty], actionable_date: Optional[ADate], due_time: ADate, source: EventSource,
            modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a person."""
        if self.source is not InboxTaskSource.PERSON_CATCH_UP:
            raise Exception(
                f"Cannot associate a task which is not recurring with a recurring one '{self.name}'")
        return self._new_version(
            project_ref_id=project_ref_id,
            name=self._build_name_for_catch_up_task(name),
            actionable_date=actionable_date,
            due_date=due_time,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=recurring_timeline,
            new_event=
            InboxTask.UpdatedLinkToPersonCatchUp.make_event_from_frame_args(source, self.version, modification_time))

    def update_link_to_person_birthday(
            self, project_ref_id: EntityId, name: InboxTaskName, recurring_timeline: str, preparation_days_cnt: int,
            due_time: ADate, source: EventSource, modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a person."""
        if self.source is not InboxTaskSource.PERSON_BIRTHDAY:
            raise Exception(
                f"Cannot associate a task which is not recurring with a recurring one '{self.name}'")
        return self._new_version(
            project_ref_id=project_ref_id,
            name=self._build_name_for_birthday_task(name),
            actionable_date=due_time.subtract_days(preparation_days_cnt),
            due_date=due_time,
            recurring_timeline=recurring_timeline,
            new_event=
            InboxTask.UpdatedLinkToPersonBirthday.make_event_from_frame_args(source, self.version, modification_time))

    def update(
            self, name: UpdateAction[InboxTaskName], status: UpdateAction[InboxTaskStatus],
            actionable_date: UpdateAction[Optional[ADate]], due_date: UpdateAction[Optional[ADate]],
            eisen: UpdateAction[Eisen], difficulty: UpdateAction[Optional[Difficulty]],
            source: EventSource, modification_time: Timestamp) -> 'InboxTask':
        """Update the inbox task."""
        return self._update(
            name=name, status=status, actionable_date=actionable_date, due_date=due_date,
            eisen=eisen, difficulty=difficulty, source=source, modification_time=modification_time,
            event_type=self.Updated)

    def update_generated(
            self, status: UpdateAction[InboxTaskStatus],
            actionable_date: UpdateAction[Optional[ADate]], due_date: UpdateAction[Optional[ADate]],
            source: EventSource, modification_time: Timestamp) -> 'InboxTask':
        """Update the inbox task parts that can be updated in a generated task."""
        return self._update(
            name=UpdateAction.do_nothing(), status=status, actionable_date=actionable_date,
            due_date=due_date, eisen=UpdateAction.do_nothing(), difficulty=UpdateAction.do_nothing(),
            source=source, modification_time=modification_time, event_type=self.UpdatedGenerated)

    def _update(
            self, name: UpdateAction[InboxTaskName], status: UpdateAction[InboxTaskStatus],
            actionable_date: UpdateAction[Optional[ADate]], due_date: UpdateAction[Optional[ADate]],
            eisen: UpdateAction[Eisen], difficulty: UpdateAction[Optional[Difficulty]],
            source: EventSource, modification_time: Timestamp, event_type: Type[AggregateRoot.Updated]) -> 'InboxTask':
        """Update the inbox task."""
        if name.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("name")
            the_name = name.value
        else:
            the_name = self.name

        the_status = self.status
        the_accepted_time = self.accepted_time
        the_working_time = self.working_time
        the_completed_time = self.completed_time
        if status.should_change:
            updated_accepted_time: UpdateAction[Optional[Timestamp]]
            if not self.status.is_accepted_or_more and status.value.is_accepted_or_more:
                the_accepted_time = modification_time
                updated_accepted_time = UpdateAction.change_to(modification_time)
            elif self.status.is_accepted_or_more and not status.value.is_accepted_or_more:
                the_accepted_time = None
                updated_accepted_time = UpdateAction.change_to(None)
            else:
                updated_accepted_time = UpdateAction.do_nothing()

            updated_working_time: UpdateAction[Optional[Timestamp]]
            if not self.status.is_working_or_more and status.value.is_working_or_more:
                the_working_time = modification_time
                updated_working_time = UpdateAction.change_to(modification_time)
            elif self.status.is_working_or_more and not status.value.is_working_or_more:
                the_working_time = None
                updated_working_time = UpdateAction.change_to(None)
            else:
                updated_working_time = UpdateAction.do_nothing()

            updated_completed_time: UpdateAction[Optional[Timestamp]]
            if not self.status.is_completed and status.value.is_completed:
                the_completed_time = modification_time
                updated_completed_time = UpdateAction.change_to(modification_time)
            elif self.status.is_completed and not status.value.is_completed:
                the_completed_time = None
                updated_completed_time = UpdateAction.change_to(None)
            else:
                updated_completed_time = UpdateAction.do_nothing()

            the_status = status.value

            event_kwargs = {
                "updated_accepted_time": updated_accepted_time,
                "updated_working_time": updated_working_time,
                "updated_completed_time": updated_completed_time
            }
        else:
            event_kwargs = {}

        if actionable_date.should_change or due_date.should_change:
            the_actionable_date = actionable_date.or_else(self.actionable_date)
            the_due_date = due_date.or_else(self.due_date)
            InboxTask._check_actionable_and_due_dates(the_actionable_date, the_due_date)
        else:
            the_actionable_date = self.actionable_date
            the_due_date = self.due_date

        if eisen.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("eisen")
            the_eisen = eisen.value
        else:
            the_eisen = self.eisen

        if difficulty.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("difficulty")
            the_difficulty = difficulty.value
        else:
            the_difficulty = self.difficulty

        return self._new_version(
            name=the_name,
            status=the_status,
            actionable_date=the_actionable_date,
            due_date=the_due_date,
            accepted_time=the_accepted_time,
            working_time=the_working_time,
            completed_time=the_completed_time,
            eisen=the_eisen,
            difficulty=the_difficulty,
            new_event=event_type.make_event_from_frame_args(source, self.version, modification_time, **event_kwargs))

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for an inbox task."""
        return self.source.allow_user_changes

    @property
    def recurring_period(self) -> Optional[RecurringTaskPeriod]:
        """The period for the recurring task, if this is such a task."""
        # TODO(horia141): fix this other massive hack!
        if self.recurring_timeline is None:
            return None
        timeline_chunks = len(self.recurring_timeline.split(","))
        if timeline_chunks == 5:
            return RecurringTaskPeriod.DAILY
        elif timeline_chunks == 4:
            return RecurringTaskPeriod.WEEKLY
        elif timeline_chunks == 3:
            return RecurringTaskPeriod.MONTHLY
        elif timeline_chunks == 2:
            return RecurringTaskPeriod.QUARTERLY
        else:
            return RecurringTaskPeriod.YEARLY

    @staticmethod
    def _build_name_for_collection_task(name: InboxTaskName) -> InboxTaskName:
        return InboxTaskName.from_raw(f"Collect value for metric {name}")

    @staticmethod
    def _build_name_for_catch_up_task(name: InboxTaskName) -> InboxTaskName:
        return InboxTaskName.from_raw(f"Catch up with {name}")

    @staticmethod
    def _build_name_for_birthday_task(name: InboxTaskName) -> InboxTaskName:
        return InboxTaskName.from_raw(f"Wish happy birthday to {name}")

    @staticmethod
    def _check_actionable_and_due_dates(actionable_date: Optional[ADate], due_date: Optional[ADate]) -> None:
        if actionable_date is None or due_date is None:
            return

        actionable_date_ts = actionable_date if isinstance(actionable_date, pendulum.DateTime) else \
            pendulum.DateTime(actionable_date.year, actionable_date.month, actionable_date.day, tzinfo=UTC)
        due_date_ts = due_date if isinstance(due_date, pendulum.DateTime) else \
            pendulum.DateTime(due_date.year, due_date.month, due_date.day, tzinfo=UTC)

        if actionable_date_ts > due_date_ts:
            raise Exception(
                f"The actionable date {actionable_date} should be before the due date {due_date}")
