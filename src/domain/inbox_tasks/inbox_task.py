"""An inbox task."""
from dataclasses import dataclass
from typing import Optional, List

import pendulum
from pendulum import UTC

from domain.adate import ADate
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.errors import ServiceValidationError
from domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_type import RecurringTaskType
from domain.timestamp import Timestamp
from framework.update_action import UpdateAction
from framework.aggregate_root import AggregateRoot
from framework.entity_id import EntityId, BAD_REF_ID
from framework.event import Event2


@dataclass()
class InboxTask(AggregateRoot):
    """An inbox task."""

    @dataclass(frozen=True)
    class Created(Event2):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Event2):
        """Updated event."""

    _inbox_task_collection_ref_id: EntityId
    _source: InboxTaskSource
    _big_plan_ref_id: Optional[EntityId]
    _recurring_task_ref_id: Optional[EntityId]
    _metric_ref_id: Optional[EntityId]
    _person_ref_id: Optional[EntityId]
    _name: EntityName
    _status: InboxTaskStatus
    _eisen: List[Eisen]
    _difficulty: Optional[Difficulty]
    _actionable_date: Optional[ADate]
    _due_date: Optional[ADate]
    _recurring_timeline: Optional[str]
    _recurring_type: Optional[RecurringTaskType]
    _recurring_gen_right_now: Optional[Timestamp]  # Time for which this inbox task was generated
    _accepted_time: Optional[Timestamp]
    _working_time: Optional[Timestamp]
    _completed_time: Optional[Timestamp]

    @staticmethod
    def new_inbox_task(
            inbox_task_collection_ref_id: EntityId, archived: bool, name: EntityName, status: InboxTaskStatus,
            big_plan_ref_id: Optional[EntityId], eisen: List[Eisen], difficulty: Optional[Difficulty],
            actionable_date: Optional[ADate], due_date: Optional[ADate], created_time: Timestamp) -> 'InboxTask':
        """Created an inbox task."""
        InboxTask._check_actionable_and_due_dates(actionable_date, due_date)

        inbox_task = InboxTask(
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            _inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            _source=InboxTaskSource.USER if big_plan_ref_id is None else InboxTaskSource.BIG_PLAN,
            _big_plan_ref_id=big_plan_ref_id,
            _recurring_task_ref_id=None,
            _metric_ref_id=None,
            _person_ref_id=None,
            _name=name,
            _status=status,
            _eisen=eisen,
            _difficulty=difficulty,
            _actionable_date=actionable_date,
            _due_date=due_date,
            _recurring_timeline=None,
            _recurring_type=None,
            _recurring_gen_right_now=None,
            _accepted_time=created_time if status.is_accepted_or_more else None,
            _working_time=created_time if status.is_working_or_more else None,
            _completed_time=created_time if status.is_completed else None)
        inbox_task.record_event(Event2.make_event_from_frame_args(InboxTask.Created, created_time))

        return inbox_task

    @staticmethod
    def new_inbox_task_for_recurring_task(
            inbox_task_collection_ref_id: EntityId, name: EntityName, recurring_task_ref_id: EntityId,
            recurring_task_timeline: str, recurring_task_type: RecurringTaskType,
            recurring_task_gen_right_now: Timestamp, eisen: List[Eisen], difficulty: Optional[Difficulty],
            actionable_date: Optional[ADate], due_date: Optional[ADate], created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            _source=InboxTaskSource.RECURRING_TASK,
            _big_plan_ref_id=None,
            _recurring_task_ref_id=recurring_task_ref_id,
            _metric_ref_id=None,
            _person_ref_id=None,
            _name=name,
            _status=InboxTaskStatus.RECURRING,
            _eisen=eisen,
            _difficulty=difficulty,
            _actionable_date=actionable_date,
            _due_date=due_date,
            _recurring_timeline=recurring_task_timeline,
            _recurring_type=recurring_task_type,
            _recurring_gen_right_now=recurring_task_gen_right_now,
            _accepted_time=created_time,
            _working_time=None,
            _completed_time=None)
        inbox_task.record_event(Event2.make_event_from_frame_args(InboxTask.Created, created_time))

        return inbox_task

    @staticmethod
    def new_inbox_task_for_metric(
            inbox_task_collection_ref_id: EntityId, name: EntityName, metric_ref_id: EntityId,
            recurring_task_timeline: str, recurring_task_gen_right_now: Timestamp, eisen: List[Eisen],
            difficulty: Optional[Difficulty], actionable_date: Optional[ADate],
            due_date: Optional[ADate], created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            _source=InboxTaskSource.METRIC,
            _big_plan_ref_id=None,
            _recurring_task_ref_id=None,
            _metric_ref_id=metric_ref_id,
            _person_ref_id=None,
            _name=InboxTask._build_name_for_collection_task(name),
            _status=InboxTaskStatus.RECURRING,
            _eisen=eisen,
            _difficulty=difficulty,
            _actionable_date=actionable_date,
            _due_date=due_date,
            _recurring_timeline=recurring_task_timeline,
            _recurring_type=RecurringTaskType.CHORE,
            _recurring_gen_right_now=recurring_task_gen_right_now,
            _accepted_time=created_time,
            _working_time=None,
            _completed_time=None)
        inbox_task.record_event(Event2.make_event_from_frame_args(InboxTask.Created, created_time))

        return inbox_task

    @staticmethod
    def new_inbox_task_for_person_catch_up(
            inbox_task_collection_ref_id: EntityId, name: EntityName, person_ref_id: EntityId,
            recurring_task_timeline: str, eisen: List[Eisen],
            difficulty: Optional[Difficulty], recurring_task_gen_right_now: Timestamp, actionable_date: Optional[ADate],
            due_date: Optional[ADate], created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            _source=InboxTaskSource.PERSON_CATCH_UP,
            _big_plan_ref_id=None,
            _recurring_task_ref_id=None,
            _metric_ref_id=None,
            _person_ref_id=person_ref_id,
            _name=InboxTask._build_name_for_catch_up_task(name),
            _status=InboxTaskStatus.RECURRING,
            _eisen=eisen,
            _difficulty=difficulty,
            _actionable_date=actionable_date,
            _due_date=due_date,
            _recurring_timeline=recurring_task_timeline,
            _recurring_type=RecurringTaskType.CHORE,
            _recurring_gen_right_now=recurring_task_gen_right_now,
            _accepted_time=created_time,
            _working_time=None,
            _completed_time=None)
        inbox_task.record_event(Event2.make_event_from_frame_args(InboxTask.Created, created_time))

        return inbox_task

    @staticmethod
    def new_inbox_task_for_person_birthday(
            inbox_task_collection_ref_id: EntityId, name: EntityName, person_ref_id: EntityId,
            recurring_task_timeline: str, recurring_task_gen_right_now: Timestamp, preparation_days_cnt: int,
            due_date: ADate, created_time: Timestamp) -> 'InboxTask':
        """Create an inbox task."""
        inbox_task = InboxTask(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _inbox_task_collection_ref_id=inbox_task_collection_ref_id,
            _source=InboxTaskSource.PERSON_BIRTHDAY,
            _big_plan_ref_id=None,
            _recurring_task_ref_id=None,
            _metric_ref_id=None,
            _person_ref_id=person_ref_id,
            _name=InboxTask._build_name_for_birthday_task(name),
            _status=InboxTaskStatus.RECURRING,
            _eisen=[Eisen.IMPORTANT],
            _difficulty=Difficulty.EASY,
            _actionable_date=due_date.subtract_days(preparation_days_cnt),
            _due_date=due_date,
            _recurring_timeline=recurring_task_timeline,
            _recurring_type=RecurringTaskType.CHORE,
            _recurring_gen_right_now=recurring_task_gen_right_now,
            _accepted_time=created_time,
            _working_time=None,
            _completed_time=None)
        inbox_task.record_event(Event2.make_event_from_frame_args(InboxTask.Created, created_time))

        return inbox_task

    def change_project(self, inbox_task_collection: InboxTaskCollection, modification_time: Timestamp) -> 'InboxTask':
        """Change the project for the inbox task."""
        if self._inbox_task_collection_ref_id == inbox_task_collection.ref_id:
            return self
        self._inbox_task_collection_ref_id = inbox_task_collection.ref_id
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def associate_with_big_plan(
            self, big_plan_ref_id: Optional[EntityId],
            big_plan_name: Optional[EntityName], modification_time: Timestamp) -> 'InboxTask':
        """Associate an inbox task with a big plan."""
        if big_plan_ref_id is None and big_plan_name is not None:
            raise ServiceValidationError(f"Should have null name for null big plan for task with id='{self.ref_id}'")
        if big_plan_ref_id is not None and big_plan_name is None:
            raise ServiceValidationError(
                f"Should have non-null name for non-null big plan for task with id='{self.ref_id}'")

        if not self._source.allow_user_changes:
            raise ServiceValidationError(
                f"Cannot modify name of task created from recurring task {self._name}")

        self._source = InboxTaskSource.BIG_PLAN
        self._big_plan_ref_id = big_plan_ref_id
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def update_link_to_big_plan(self, big_plan_ref_id: EntityId, modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a big plan."""
        if self._source is not InboxTaskSource.BIG_PLAN:
            raise ServiceValidationError(
                f"Cannot reassociate a task which isn't a big plan one '{self._name}'")
        if self._big_plan_ref_id != big_plan_ref_id:
            raise ServiceValidationError(
                f"Cannot reassociate a task which is not with the big plan '{self._name}'")

        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def update_link_to_recurring_task(self, name: EntityName, timeline: str, the_type: RecurringTaskType,
                                      actionable_date: Optional[ADate], due_time: ADate, eisen: List[Eisen],
                                      difficulty: Optional[Difficulty], modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a recurring task."""
        if self._source is not InboxTaskSource.RECURRING_TASK:
            raise ServiceValidationError(
                f"Cannot associate a task which is not recurring with a recurring one '{self._name}'")
        self._name = name
        self._actionable_date = actionable_date
        self._due_date = due_time
        self._eisen = eisen
        self._difficulty = difficulty
        self._recurring_timeline = timeline
        self._recurring_type = the_type
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def update_link_to_metric(
            self, name: EntityName, recurring_timeline: str, eisen: List[Eisen], difficulty: Optional[Difficulty],
            actionable_date: Optional[ADate], due_time: ADate, modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a metric."""
        if self._source is not InboxTaskSource.METRIC:
            raise ServiceValidationError(
                f"Cannot associate a task which is not recurring with a recurring one '{self._name}'")
        self._name = self._build_name_for_collection_task(name)
        self._actionable_date = actionable_date
        self._due_date = due_time
        self._eisen = eisen
        self._difficulty = difficulty
        self._recurring_timeline = recurring_timeline
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def update_link_to_person_catch_up(
            self, name: EntityName, recurring_timeline: str, eisen: List[Eisen], difficulty: Optional[Difficulty],
            actionable_date: Optional[ADate], due_time: ADate, modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a person."""
        if self._source is not InboxTaskSource.PERSON_CATCH_UP:
            raise ServiceValidationError(
                f"Cannot associate a task which is not recurring with a recurring one '{self._name}'")
        self._name = self._build_name_for_catch_up_task(name)
        self._actionable_date = actionable_date
        self._due_date = due_time
        self._eisen = eisen
        self._difficulty = difficulty
        self._recurring_timeline = recurring_timeline
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def update_link_to_person_birthday(
            self, name: EntityName, recurring_timeline: str, preparation_days_cnt: int,
            due_time: ADate, modification_time: Timestamp) -> 'InboxTask':
        """Update all the info associated with a person."""
        if self._source is not InboxTaskSource.PERSON_BIRTHDAY:
            raise ServiceValidationError(
                f"Cannot associate a task which is not recurring with a recurring one '{self._name}'")
        self._name = self._build_name_for_birthday_task(name)
        self._actionable_date = due_time.subtract_days(preparation_days_cnt)
        self._due_date = due_time
        self._recurring_timeline = recurring_timeline
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'InboxTask':
        """Change the name of the inbox task."""
        if not self._source.allow_user_changes:
            raise ServiceValidationError(
                f"Cannot modify name of task created from recurring task {self._name}")
        if self._name == name:
            return self
        self._name = name
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def change_status(self, status: InboxTaskStatus, modification_time: Timestamp) -> 'InboxTask':
        """Change the status of the inbox task."""
        if self._status == status:
            return self

        updated_accepted_time: UpdateAction[Optional[Timestamp]]
        if not self._status.is_accepted_or_more and status.is_accepted_or_more:
            self._accepted_time = modification_time
            updated_accepted_time = UpdateAction.change_to(modification_time)
        elif self._status.is_accepted_or_more and not status.is_accepted_or_more:
            self._accepted_time = None
            updated_accepted_time = UpdateAction.change_to(None)
        else:
            updated_accepted_time = UpdateAction.do_nothing()

        updated_working_time: UpdateAction[Optional[Timestamp]]
        if not self._status.is_working_or_more and status.is_working_or_more:
            self._working_time = modification_time
            updated_working_time = UpdateAction.change_to(modification_time)
        elif self._status.is_working_or_more and not status.is_working_or_more:
            self._working_time = None
            updated_working_time = UpdateAction.change_to(None)
        else:
            updated_working_time = UpdateAction.do_nothing()

        updated_completed_time: UpdateAction[Optional[Timestamp]]
        if not self._status.is_completed and status.is_completed:
            self._completed_time = modification_time
            updated_completed_time = UpdateAction.change_to(modification_time)
        elif self._status.is_completed and not status.is_completed:
            self._completed_time = None
            updated_completed_time = UpdateAction.change_to(None)
        else:
            updated_completed_time = UpdateAction.do_nothing()

        self._status = status
        self.record_event(Event2.make_event_from_frame_args(
            InboxTask.Updated, modification_time, updated_accepted_time=updated_accepted_time,
            updated_working_time=updated_working_time, updated_completed_time=updated_completed_time))
        return self

    def change_actionable_date(self, actionable_date: Optional[ADate], modification_time: Timestamp) -> 'InboxTask':
        """Change the actionable date of the inbox task."""
        InboxTask._check_actionable_and_due_dates(actionable_date, self._due_date)
        if self._actionable_date == actionable_date:
            return self
        self._actionable_date = actionable_date
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def change_due_date(self, due_date: Optional[ADate], modification_time: Timestamp) -> 'InboxTask':
        """Change the due date of the inbox task."""
        InboxTask._check_actionable_and_due_dates(self._actionable_date, due_date)
        if self._due_date == due_date:
            return self
        self._due_date = due_date
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def change_eisen(self, eisen: List[Eisen], modification_time: Timestamp) -> 'InboxTask':
        """Change the eisen status of the inbox task."""
        if not self._source.allow_user_changes:
            raise ServiceValidationError(
                f"Cannot modify name of task created from recurring task {self._name}")
        if set(self._eisen) == set(eisen):
            return self
        self._eisen = eisen
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    def change_difficulty(self, difficulty: Optional[Difficulty], modification_time: Timestamp) -> 'InboxTask':
        """Change the difficulty of the inbox task."""
        if not self._source.allow_user_changes:
            raise ServiceValidationError(
                f"Cannot modify name of task created from recurring task {self._name}")
        if self._difficulty == difficulty:
            return self
        self._difficulty = difficulty
        self.record_event(Event2.make_event_from_frame_args(InboxTask.Updated, modification_time))
        return self

    @property
    def project_ref_id(self) -> EntityId:
        """The project this task belong to."""
        # TODO(horia141): fix this uglyness
        return self._inbox_task_collection_ref_id

    @property
    def inbox_task_collection_ref_id(self) -> EntityId:
        """The inbox task collection this inbox task belongs to."""
        return self._inbox_task_collection_ref_id

    @property
    def source(self) -> InboxTaskSource:
        """The source of the inbox task."""
        return self._source

    @property
    def big_plan_ref_id(self) -> Optional[EntityId]:
        """The big plan this inbox task belongs to, if any."""
        return self._big_plan_ref_id

    @property
    def recurring_task_ref_id(self) -> Optional[EntityId]:
        """The recurring task this inbox task belongs to, if any."""
        return self._recurring_task_ref_id

    @property
    def metric_ref_id(self) -> Optional[EntityId]:
        """The metric this inbox task belongs to, if any."""
        return self._metric_ref_id

    @property
    def person_ref_id(self) -> Optional[EntityId]:
        """The person this inbox task belongs to, if any."""
        return self._person_ref_id

    @property
    def name(self) -> EntityName:
        """The name."""
        return self._name

    @property
    def status(self) -> InboxTaskStatus:
        """The working status."""
        return self._status

    @property
    def eisen(self) -> List[Eisen]:
        """The Eisenhower categories for this inbox task."""
        return self._eisen


    @property
    def difficulty(self) -> Optional[Difficulty]:
        """The difficulty of this inbox task."""
        return self._difficulty

    @property
    def actionable_date(self) -> Optional[ADate]:
        """The date work can begin on this task, or None if immediately."""
        return self._actionable_date

    @property
    def due_date(self) -> Optional[ADate]:
        """The date this task needs to be done, or None if no pressure."""
        return self._due_date

    @property
    def recurring_timeline(self) -> Optional[str]:
        """The timeline into for recurring task, if this is such a task."""
        return self._recurring_timeline

    @property
    def recurring_period(self) -> Optional[RecurringTaskPeriod]:
        """The period for the recurring task, if this is such a task."""
        # TODO(horia141): fix this other massive hack!
        if self._recurring_timeline is None:
            return None
        timeline_chunks = len(self._recurring_timeline.split(","))
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

    @property
    def recurring_type(self) -> Optional[RecurringTaskType]:
        """The type of recurring task this was generated from."""
        return self._recurring_type

    @property
    def recurring_gen_right_now(self) -> Optional[Timestamp]:
        """The time this task was first generated on."""
        return self._recurring_gen_right_now

    @property
    def accepted_time(self) -> Optional[Timestamp]:
        """The time this task was accepted for work."""
        return self._accepted_time

    @property
    def working_time(self) -> Optional[Timestamp]:
        """The time this task was actually started."""
        return self._working_time

    @property
    def completed_time(self) -> Optional[Timestamp]:
        """The time this task was completed."""
        return self._completed_time

    @staticmethod
    def _build_name_for_collection_task(name: EntityName) -> EntityName:
        return EntityName.from_raw(f"Collect value for metric {name}")

    @staticmethod
    def _build_name_for_catch_up_task(name: EntityName) -> EntityName:
        return EntityName.from_raw(f"Catch up with {name}")

    @staticmethod
    def _build_name_for_birthday_task(name: EntityName) -> EntityName:
        return EntityName.from_raw(f"Wish happy birthday to {name}")

    @staticmethod
    def _check_actionable_and_due_dates(actionable_date: Optional[ADate], due_date: Optional[ADate]) -> None:
        if actionable_date is None or due_date is None:
            return

        actionable_date_ts = actionable_date if isinstance(actionable_date, pendulum.DateTime) else \
            pendulum.DateTime(actionable_date.year, actionable_date.month, actionable_date.day, tzinfo=UTC)
        due_date_ts = due_date if isinstance(due_date, pendulum.DateTime) else \
            pendulum.DateTime(due_date.year, due_date.month, due_date.day, tzinfo=UTC)

        if actionable_date_ts > due_date_ts:
            raise ServiceValidationError(
                f"The actionable date {actionable_date} should be before the due date {due_date}")
