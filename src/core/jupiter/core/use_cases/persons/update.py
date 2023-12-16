"""Update a person."""
import typing
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class PersonUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[PersonName]
    relationship: UpdateAction[PersonRelationship]
    catch_up_period: UpdateAction[Optional[RecurringTaskPeriod]]
    catch_up_eisen: UpdateAction[Optional[Eisen]]
    catch_up_difficulty: UpdateAction[Optional[Difficulty]]
    catch_up_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    catch_up_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    catch_up_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
    catch_up_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    catch_up_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    birthday: UpdateAction[Optional[PersonBirthday]]


class PersonUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonUpdateArgs, None]
):
    """The command for updating a person."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.PERSONS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: PersonUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        person_collection = await uow.person_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        person = await uow.person_repository.load_by_id(args.ref_id)

        # Change the person.
        catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]]
        if (
            args.catch_up_period.should_change
            or args.catch_up_eisen.should_change
            or args.catch_up_difficulty.should_change
            or args.catch_up_actionable_from_day.should_change
            or args.catch_up_actionable_from_month.should_change
            or args.catch_up_due_at_time.should_change
            or args.catch_up_due_at_day.should_change
            or args.catch_up_due_at_month
        ):
            new_catch_up_period = None
            if args.catch_up_period.should_change:
                new_catch_up_period = args.catch_up_period.just_the_value
            elif person.catch_up_params is not None:
                new_catch_up_period = person.catch_up_params.period

            if new_catch_up_period is not None:
                new_catch_up_eisen = None
                if args.catch_up_eisen.should_change:
                    new_catch_up_eisen = args.catch_up_eisen.just_the_value
                elif person.catch_up_params is not None:
                    new_catch_up_eisen = person.catch_up_params.eisen

                new_catch_up_difficulty = None
                if args.catch_up_difficulty.should_change:
                    new_catch_up_difficulty = args.catch_up_difficulty.just_the_value
                elif person.catch_up_params is not None:
                    new_catch_up_difficulty = person.catch_up_params.difficulty

                new_catch_up_actionable_from_day = None
                if args.catch_up_actionable_from_day.should_change:
                    new_catch_up_actionable_from_day = (
                        args.catch_up_actionable_from_day.just_the_value
                    )
                elif person.catch_up_params is not None:
                    new_catch_up_actionable_from_day = (
                        person.catch_up_params.actionable_from_day
                    )

                new_catch_up_actionable_from_month = None
                if args.catch_up_actionable_from_month.should_change:
                    new_catch_up_actionable_from_month = (
                        args.catch_up_actionable_from_month.just_the_value
                    )
                elif person.catch_up_params is not None:
                    new_catch_up_actionable_from_month = (
                        person.catch_up_params.actionable_from_month
                    )

                new_catch_up_due_at_time = None
                if args.catch_up_due_at_time.should_change:
                    new_catch_up_due_at_time = args.catch_up_due_at_time.just_the_value
                elif person.catch_up_params is not None:
                    new_catch_up_due_at_time = person.catch_up_params.due_at_time

                new_catch_up_due_at_day = None
                if args.catch_up_due_at_day.should_change:
                    new_catch_up_due_at_day = args.catch_up_due_at_day.just_the_value
                elif person.catch_up_params is not None:
                    new_catch_up_due_at_day = person.catch_up_params.due_at_day

                new_catch_up_due_at_month = None
                if args.catch_up_due_at_month.should_change:
                    new_catch_up_due_at_month = (
                        args.catch_up_due_at_month.just_the_value
                    )
                elif person.catch_up_params is not None:
                    new_catch_up_due_at_month = person.catch_up_params.due_at_month

                catch_up_params = UpdateAction.change_to(
                    RecurringTaskGenParams(
                        period=new_catch_up_period,
                        eisen=new_catch_up_eisen,
                        difficulty=new_catch_up_difficulty,
                        actionable_from_day=new_catch_up_actionable_from_day,
                        actionable_from_month=new_catch_up_actionable_from_month,
                        due_at_time=new_catch_up_due_at_time,
                        due_at_day=new_catch_up_due_at_day,
                        due_at_month=new_catch_up_due_at_month,
                    ),
                )
            else:
                catch_up_params = UpdateAction.change_to(None)
        else:
            catch_up_params = UpdateAction.do_nothing()

        project = await uow.project_repository.load_by_id(
            person_collection.catch_up_project_ref_id,
        )
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        person_catch_up_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
            filter_person_ref_ids=[person.ref_id],
        )
        person_birthday_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
            filter_person_ref_ids=[person.ref_id],
        )

        # TODO(horia141): also create tasks here!
        # TODO(horia141): what if we change other person properties not just catch up params?
        # Change the catch up inbox tasks
        if person.catch_up_params is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            inbox_task_archive_service = InboxTaskArchiveService(
                source=EventSource.CLI,
                time_provider=self._time_provider,
            )
            for inbox_task in person_catch_up_tasks:
                await inbox_task_archive_service.do_it(
                    uow, progress_reporter, inbox_task
                )
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_catch_up_tasks:
                schedule = schedules.get_schedule(
                    person.catch_up_params.period,
                    person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now),
                    user.timezone,
                    None,
                    person.catch_up_params.actionable_from_day,
                    person.catch_up_params.actionable_from_month,
                    person.catch_up_params.due_at_time,
                    person.catch_up_params.due_at_day,
                    person.catch_up_params.due_at_month,
                )

                inbox_task = inbox_task.update_link_to_person_catch_up(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    eisen=person.catch_up_params.eisen,
                    difficulty=person.catch_up_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_time,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                # Situation 2a: we're handling the same project.
                await uow.inbox_task_repository.save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

        # Change the birthday inbox tasks
        if person.birthday is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            inbox_task_archive_service = InboxTaskArchiveService(
                source=EventSource.CLI,
                time_provider=self._time_provider,
            )
            for inbox_task in person_birthday_tasks:
                await inbox_task_archive_service.do_it(
                    uow, progress_reporter, inbox_task
                )
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_birthday_tasks:
                schedule = schedules.get_schedule(
                    RecurringTaskPeriod.YEARLY,
                    person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now),
                    user.timezone,
                    None,
                    None,
                    None,
                    None,
                    RecurringTaskDueAtDay.from_raw(
                        RecurringTaskPeriod.MONTHLY,
                        person.birthday.day,
                    ),
                    RecurringTaskDueAtMonth.from_raw(
                        RecurringTaskPeriod.YEARLY,
                        person.birthday.month,
                    ),
                )

                inbox_task = inbox_task.update_link_to_person_birthday(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                    due_time=schedule.due_time,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                await uow.inbox_task_repository.save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

        person = person.update(
            name=args.name,
            relationship=args.relationship,
            birthday=args.birthday,
            catch_up_params=catch_up_params,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.person_repository.save(person)
        await progress_reporter.mark_updated(person)
