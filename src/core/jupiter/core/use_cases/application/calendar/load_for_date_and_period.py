"""Load all the calendar specific entities for a given date and period."""
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_event_full_days import (
    ScheduleEventFullDays,
)
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
    TimeEventFullDaysBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
    TimeEventInDayBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class CalendarLoadForDateAndPeriodArgs(UseCaseArgsBase):
    """Args."""

    right_now: ADate
    period: RecurringTaskPeriod
    stats_subperiod: RecurringTaskPeriod | None


@use_case_result_part
class ScheduleInDayEventEntry(UseCaseResultBase):
    """Result entry."""

    event: ScheduleEventInDay
    time_event: TimeEventInDayBlock
    stream: ScheduleStream


@use_case_result_part
class ScheduleFullDaysEventEntry(UseCaseResultBase):
    """Result entry."""

    event: ScheduleEventFullDays
    time_event: TimeEventFullDaysBlock
    stream: ScheduleStream


@use_case_result_part
class InboxTaskEntry(UseCaseResultBase):
    """Result entry."""

    inbox_task: InboxTask
    time_events: list[TimeEventInDayBlock]


@use_case_result_part
class PersonEntry(UseCaseResultBase):
    """Result entry."""

    person: Person
    birthday_time_event: TimeEventFullDaysBlock


@use_case_result_part
class CalendarEventsEntries(UseCaseResultBase):
    """Full entries for results."""

    schedule_event_full_days_entries: list[ScheduleFullDaysEventEntry]
    schedule_event_in_day_entries: list[ScheduleInDayEventEntry]
    inbox_task_entries: list[InboxTaskEntry]
    person_entries: list[PersonEntry]


@use_case_result_part
class CalendarEventsStatsPerSubperiod(UseCaseResultBase):
    """Stats about a particular subperiod."""

    period_start_date: ADate
    schedule_event_full_days_cnt: int
    schedule_event_in_day_cnt: int
    inbox_task_cnt: int
    person_birthday_cnt: int


@use_case_result_part
class CalendarEventsStats(UseCaseResultBase):
    """Stats about events in a period."""

    subperiod: RecurringTaskPeriod
    per_subperiod: list[CalendarEventsStatsPerSubperiod]


@use_case_result
class CalendarLoadForDateAndPeriodResult(UseCaseResultBase):
    """Result."""

    right_now: ADate
    period: RecurringTaskPeriod
    stats_subperiod: RecurringTaskPeriod | None
    period_start_date: ADate
    period_end_date: ADate
    prev_period_start_date: ADate
    next_period_start_date: ADate
    entries: CalendarEventsEntries | None
    stats: CalendarEventsStats | None


@readonly_use_case(WorkspaceFeature.SCHEDULE)
class CalendarLoadForDateAndPeriodUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        CalendarLoadForDateAndPeriodArgs, CalendarLoadForDateAndPeriodResult
    ]
):
    """Use case for loading all the calendar entities for a given date and period."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: CalendarLoadForDateAndPeriodArgs,
    ) -> CalendarLoadForDateAndPeriodResult:
        """Execute the action."""
        if (
            args.period is RecurringTaskPeriod.DAILY
            and args.stats_subperiod is not None
        ):
            raise InputValidationError(
                "Stats subperiod is not allowed for daily period."
            )
        elif args.stats_subperiod not in args.period.all_smaller_periods:
            raise InputValidationError(
                f"Stats subperiod {args.stats_subperiod} is not smaller than period {args.period}."
            )

        workspace = context.workspace
        schedule = schedules.get_schedule(
            period=args.period,
            right_now=args.right_now.to_timestamp_at_start_of_day(),
            name=NOT_USED_NAME,
        )
        prev_schedule = schedules.get_schedule(
            period=args.period,
            right_now=schedule.first_day.subtract_days(
                1
            ).to_timestamp_at_start_of_day(),
            name=NOT_USED_NAME,
        )
        next_schedule = schedules.get_schedule(
            period=args.period,
            right_now=schedule.end_day.add_days(1).to_timestamp_at_start_of_day(),
            name=NOT_USED_NAME,
        )

        time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
            workspace.ref_id
        )
        schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
            workspace.ref_id
        )

        schedule_streams = await uow.get_for(ScheduleStream).find_all_generic(
            parent_ref_id=schedule_domain.ref_id,
            allow_archived=False,
        )
        schedule_streams_by_ref_id: dict[EntityId, ScheduleStream] = {
            ss.ref_id: ss for ss in schedule_streams
        }

        entries: CalendarEventsEntries | None = None
        if (
            args.period is RecurringTaskPeriod.DAILY
            or args.period is RecurringTaskPeriod.WEEKLY
        ):
            entries = await self._build_entries(
                uow,
                workspace,
                schedule,
                time_event_domain,
                schedule_domain,
                schedule_streams_by_ref_id,
            )

        stats: CalendarEventsStats | None = None
        if schedule.period != RecurringTaskPeriod.DAILY:
            stats = await self._build_stats(
                uow, schedule, args.stats_subperiod, time_event_domain
            )

        return CalendarLoadForDateAndPeriodResult(
            right_now=args.right_now,
            period=args.period,
            stats_subperiod=args.stats_subperiod,
            period_start_date=schedule.first_day,
            period_end_date=schedule.end_day,
            prev_period_start_date=prev_schedule.first_day,
            next_period_start_date=next_schedule.first_day,
            entries=entries,
            stats=stats,
        )

    async def _build_entries(
        self,
        uow: DomainUnitOfWork,
        workspace: Workspace,
        schedule: schedules.Schedule,
        time_event_domain: TimeEventDomain,
        schedule_domain: ScheduleDomain,
        schedule_streams_by_ref_id: dict[EntityId, ScheduleStream],
    ) -> CalendarEventsEntries:
        time_events_full_days: list[TimeEventFullDaysBlock] = await uow.get(
            TimeEventFullDaysBlockRepository
        ).find_all_between(
            parent_ref_id=time_event_domain.ref_id,
            start_date=schedule.first_day,
            end_date=schedule.end_day,
        )

        time_events_in_day: list[TimeEventInDayBlock] = await uow.get(
            TimeEventInDayBlockRepository
        ).find_all_between(
            parent_ref_id=time_event_domain.ref_id,
            # Events can be at most 48hrs long, and to catch those that start before the period
            # but end inside it we have this little approach.
            start_date=schedule.first_day.subtract_days(2),
            end_date=schedule.end_day,
        )

        time_events_full_days_for_schedule_events_full_days: dict[
            EntityId, TimeEventFullDaysBlock
        ] = {
            te.source_entity_ref_id: te
            for te in time_events_full_days
            if te.namespace == TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK
        }
        schedule_events_full_days = []
        if len(time_events_full_days_for_schedule_events_full_days) > 0:
            schedule_events_full_days = await uow.get_for(
                ScheduleEventFullDays
            ).find_all_generic(
                parent_ref_id=schedule_domain.ref_id,
                allow_archived=False,
                ref_id=list(time_events_full_days_for_schedule_events_full_days.keys()),
            )
        schedule_event_full_days_entries = [
            ScheduleFullDaysEventEntry(
                event=se,
                time_event=time_events_full_days_for_schedule_events_full_days[
                    se.ref_id
                ],
                stream=schedule_streams_by_ref_id[se.schedule_stream_ref_id],
            )
            for se in schedule_events_full_days
        ]

        time_events_in_day_for_schedule_events_in_day: dict[
            EntityId, TimeEventInDayBlock
        ] = {
            te.source_entity_ref_id: te
            for te in time_events_in_day
            if te.namespace == TimeEventNamespace.SCHEDULE_EVENT_IN_DAY
        }
        schedule_events_in_day = []
        if len(time_events_in_day_for_schedule_events_in_day) > 0:
            schedule_events_in_day = await uow.get_for(
                ScheduleEventInDay
            ).find_all_generic(
                parent_ref_id=schedule_domain.ref_id,
                allow_archived=False,
                ref_id=list(time_events_in_day_for_schedule_events_in_day.keys()),
            )
        schedule_event_in_day_entries = [
            ScheduleInDayEventEntry(
                event=se,
                time_event=time_events_in_day_for_schedule_events_in_day[se.ref_id],
                stream=schedule_streams_by_ref_id[se.schedule_stream_ref_id],
            )
            for se in schedule_events_in_day
        ]

        time_events_in_day_for_inbox_tasks: dict[
            EntityId, list[TimeEventInDayBlock]
        ] = {
            te.source_entity_ref_id: []
            for te in time_events_in_day
            if te.namespace == TimeEventNamespace.INBOX_TASK
        }
        for te in time_events_in_day:
            if te.namespace == TimeEventNamespace.INBOX_TASK:
                time_events_in_day_for_inbox_tasks[te.source_entity_ref_id].append(te)
        inbox_tasks = []
        if len(time_events_in_day_for_inbox_tasks) > 0:
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=workspace.ref_id,
                allow_archived=False,
                ref_id=list(time_events_in_day_for_inbox_tasks.keys()),
            )
        inbox_task_entries = [
            InboxTaskEntry(
                inbox_task=inbox_task,
                time_events=time_events_in_day_for_inbox_tasks[inbox_task.ref_id],
            )
            for inbox_task in inbox_tasks
        ]

        time_events_full_days_for_persons: dict[EntityId, TimeEventFullDaysBlock] = {
            te.source_entity_ref_id: te
            for te in time_events_full_days
            if te.namespace == TimeEventNamespace.PERSON_BIRTHDAY
        }
        persons = []
        if len(time_events_full_days_for_persons) > 0:
            persons = await uow.get_for(Person).find_all_generic(
                parent_ref_id=workspace.ref_id,
                allow_archived=False,
                ref_id=list(time_events_full_days_for_persons.keys()),
            )
        person_entries = [
            PersonEntry(
                person=person,
                birthday_time_event=time_events_full_days_for_persons[person.ref_id],
            )
            for person in persons
        ]

        entries = CalendarEventsEntries(
            schedule_event_full_days_entries=schedule_event_full_days_entries,
            schedule_event_in_day_entries=schedule_event_in_day_entries,
            inbox_task_entries=inbox_task_entries,
            person_entries=person_entries,
        )

        return entries

    async def _build_stats(
        self,
        uow: DomainUnitOfWork,
        schedule: schedules.Schedule,
        stats_subperiod: RecurringTaskPeriod,
        time_event_domain: TimeEventDomain,
    ) -> CalendarEventsStats:
        full_days_raw_stats = await uow.get(
            TimeEventFullDaysBlockRepository
        ).stats_for_all_between(
            parent_ref_id=time_event_domain.ref_id,
            start_date=schedule.first_day,
            end_date=schedule.end_day,
        )
        in_day_raw_stats = await uow.get(
            TimeEventInDayBlockRepository
        ).stats_for_all_between(
            parent_ref_id=time_event_domain.ref_id,
            start_date=schedule.first_day,
            end_date=schedule.end_day,
        )

        per_subperiod = []
        curr_day = schedule.first_day
        while curr_day <= schedule.end_day:
            subschedule = schedules.get_schedule(
                period=stats_subperiod,
                right_now=curr_day.to_timestamp_at_start_of_day(),
                name=NOT_USED_NAME,
            )

            schedule_event_full_days_cnt = 0
            schedule_event_in_day_cnt = 0
            inbox_task_cnt = 0
            person_birthday_cnt = 0

            # This is O(N*M) with a rather small M, so it's fine. Probably faster due to memory locality boosts.
            for full_days_stats in full_days_raw_stats.per_groups:
                if (
                    full_days_stats.date >= subschedule.first_day
                    and full_days_stats.date <= subschedule.end_day
                ):
                    if (
                        full_days_stats.namespace
                        == TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK
                    ):
                        schedule_event_full_days_cnt += full_days_stats.cnt
                    elif (
                        full_days_stats.namespace == TimeEventNamespace.PERSON_BIRTHDAY
                    ):
                        person_birthday_cnt += full_days_stats.cnt
            for in_day_stats in in_day_raw_stats.per_groups:
                if (
                    in_day_stats.date >= subschedule.first_day
                    and in_day_stats.date <= subschedule.end_day
                ):
                    if (
                        in_day_stats.namespace
                        == TimeEventNamespace.SCHEDULE_EVENT_IN_DAY
                    ):
                        schedule_event_in_day_cnt += in_day_stats.cnt
                    elif in_day_stats.namespace == TimeEventNamespace.INBOX_TASK:
                        inbox_task_cnt += in_day_stats.cnt

            per_subperiod.append(
                CalendarEventsStatsPerSubperiod(
                    period_start_date=curr_day,
                    schedule_event_full_days_cnt=schedule_event_full_days_cnt,
                    schedule_event_in_day_cnt=schedule_event_in_day_cnt,
                    inbox_task_cnt=inbox_task_cnt,
                    person_birthday_cnt=person_birthday_cnt,
                )
            )

            curr_day = subschedule.end_day.add_days(1)

        stats: CalendarEventsStats = CalendarEventsStats(
            subperiod=stats_subperiod,
            per_subperiod=per_subperiod,
        )

        return stats
