"""Update a person."""
import typing
from typing import Optional

from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
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
    catch_up_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    catch_up_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    birthday: UpdateAction[Optional[PersonBirthday]]


@mutation_use_case(WorkspaceFeature.PERSONS)
class PersonUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonUpdateArgs, None]
):
    """The command for updating a person."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: PersonUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.repository_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        person = await uow.repository_for(Person).load_by_id(args.ref_id)

        # Change the person.
        catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]]
        if (
            args.catch_up_period.should_change
            or args.catch_up_eisen.should_change
            or args.catch_up_difficulty.should_change
            or args.catch_up_actionable_from_day.should_change
            or args.catch_up_actionable_from_month.should_change
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
                        due_at_day=new_catch_up_due_at_day,
                        due_at_month=new_catch_up_due_at_month,
                    ),
                )
            else:
                catch_up_params = UpdateAction.change_to(None)
        else:
            catch_up_params = UpdateAction.do_nothing()

        project = await uow.repository_for(Project).load_by_id(
            person_collection.catch_up_project_ref_id,
        )
        inbox_task_collection = await uow.repository_for(
            InboxTaskCollection
        ).load_by_parent(
            workspace.ref_id,
        )
        person_catch_up_tasks = await uow.repository_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=[InboxTaskSource.PERSON_CATCH_UP],
            person_ref_id=[person.ref_id],
        )
        person_birthday_tasks = await uow.repository_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=[InboxTaskSource.PERSON_BIRTHDAY],
            person_ref_id=[person.ref_id],
        )

        # TODO(horia141): also create tasks here!
        # TODO(horia141): what if we change other person properties not just catch up params?
        # Change the catch up inbox tasks
        if person.catch_up_params is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            inbox_task_archive_service = InboxTaskArchiveService()
            for inbox_task in person_catch_up_tasks:
                await inbox_task_archive_service.do_it(
                    context.domain_context, uow, progress_reporter, inbox_task
                )
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_catch_up_tasks:
                schedule = schedules.get_schedule(
                    person.catch_up_params.period,
                    person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now),
                    None,
                    person.catch_up_params.actionable_from_day,
                    person.catch_up_params.actionable_from_month,
                    person.catch_up_params.due_at_day,
                    person.catch_up_params.due_at_month,
                )

                inbox_task = inbox_task.update_link_to_person_catch_up(
                    ctx=context.domain_context,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    eisen=person.catch_up_params.eisen,
                    difficulty=person.catch_up_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_date,
                )
                # Situation 2a: we're handling the same project.
                await uow.repository_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

        # Change the birthday inbox tasks
        if person.birthday is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            inbox_task_archive_service = InboxTaskArchiveService()
            for inbox_task in person_birthday_tasks:
                await inbox_task_archive_service.do_it(
                    context.domain_context, uow, progress_reporter, inbox_task
                )
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_birthday_tasks:
                schedule = schedules.get_schedule(
                    RecurringTaskPeriod.YEARLY,
                    person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now),
                    None,
                    None,
                    None,
                    RecurringTaskDueAtDay(
                        RecurringTaskPeriod.YEARLY,
                        person.birthday.day,
                    ),
                    RecurringTaskDueAtMonth(
                        RecurringTaskPeriod.YEARLY,
                        person.birthday.month,
                    ),
                )

                inbox_task = inbox_task.update_link_to_person_birthday(
                    ctx=context.domain_context,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                    due_time=schedule.due_date,
                )

                await uow.repository_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

        person = person.update(
            ctx=context.domain_context,
            name=args.name,
            relationship=args.relationship,
            birthday=args.birthday,
            catch_up_params=catch_up_params,
        )

        await uow.repository_for(Person).save(person)
        await progress_reporter.mark_updated(person)
