"""UseCase for updating a person."""
from argparse import ArgumentParser, Namespace
from typing import Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.persons.update import PersonUpdateArgs, PersonUpdateUseCase


class PersonUpdate(LoggedInMutationCommand[PersonUpdateUseCase]):
    """UseCase class for updating a person."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "person-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a person"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the person",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            help="The name of the person",
        )
        parser.add_argument(
            "--relationship",
            dest="relationship",
            required=False,
            choices=PersonRelationship.all_values(),
            help="The person's relationship to you",
        )
        catch_up_project = parser.add_mutually_exclusive_group()
        catch_up_project.add_argument(
            "--catch-up-project",
            dest="catch_up_project_key",
            required=False,
            help="The project key to generate recurring catch up tasks",
        )
        catch_up_project.add_argument(
            "--clear-catch-up-project",
            dest="clear_catch_up_project_key",
            required=False,
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up project",
        )
        catch_up_period = parser.add_mutually_exclusive_group()
        catch_up_period.add_argument(
            "--catch-up-period",
            dest="catch_up_period",
            required=False,
            choices=RecurringTaskPeriod.all_values(),
            help="The period at which a metric should be recorded",
        )
        catch_up_period.add_argument(
            "--clear-catch-up-period",
            dest="clear_catch_up_period",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up period",
        )
        catch_up_eisen = parser.add_mutually_exclusive_group()
        catch_up_eisen.add_argument(
            "--catch-up-eisen",
            dest="catch_up_eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for catch up task",
        )
        catch_up_eisen.add_argument(
            "--clear-catch-up-eisen",
            dest="clear_catch_up_eisen",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up eisen of the metric",
        )
        catch_up_difficulty = parser.add_mutually_exclusive_group()
        catch_up_difficulty.add_argument(
            "--catch-up-difficulty",
            dest="catch_up_difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for catch up tasks",
        )
        catch_up_difficulty.add_argument(
            "--clear-catch-up-difficulty",
            dest="clear_catch_up_difficulty",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up difficulty",
        )
        catch_up_actionable_from_day = parser.add_mutually_exclusive_group()
        catch_up_actionable_from_day.add_argument(
            "--catch-up-actionable-from-day",
            type=int,
            dest="catch_up_actionable_from_day",
            metavar="DAY",
            help="The day of the interval the catch up task will be actionable from",
        )
        catch_up_actionable_from_day.add_argument(
            "--clear-catch-up-actionable-from-day",
            dest="clear_catch_up_actionable_from_day",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up actionable day",
        )
        catch_up_actionable_from_month = parser.add_mutually_exclusive_group()
        catch_up_actionable_from_month.add_argument(
            "--catch-up-actionable-from-month",
            type=int,
            dest="catch_up_actionable_from_month",
            metavar="MONTH",
            help="The month of the interval the catch up task will be actionable from",
        )
        catch_up_actionable_from_month.add_argument(
            "--clear-catch-up-actionable-from-month",
            dest="clear_catch_up_actionable_from_month",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up actionable month",
        )
        catch_up_due_at_time = parser.add_mutually_exclusive_group()
        catch_up_due_at_time.add_argument(
            "--catch-up-due-at-time",
            dest="catch_up_due_at_time",
            metavar="HH:MM",
            help="The time a task will be due on",
        )
        catch_up_due_at_time.add_argument(
            "--clear-catch-up-due-at-time",
            dest="clear_catch_up_due_at_time",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up due time",
        )
        catch_up_due_at_day = parser.add_mutually_exclusive_group()
        catch_up_due_at_day.add_argument(
            "--catch-up-due-at-day",
            type=int,
            dest="catch_up_due_at_day",
            metavar="DAY",
            help="The day of the interval the catch up task will be due on",
        )
        catch_up_due_at_day.add_argument(
            "--clear-catch-up-due-at-day",
            dest="clear_catch_up_due_at_day",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up due day",
        )
        catch_up_due_at_month = parser.add_mutually_exclusive_group()
        catch_up_due_at_month.add_argument(
            "--catch-up-due-at-month",
            type=int,
            dest="catch_up_due_at_month",
            metavar="MONTH",
            help="The month of the interval the catch up task will be due on",
        )
        catch_up_due_at_month.add_argument(
            "--clear-catch-up-due-at-month",
            dest="clear_catch_up_due_at_month",
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up due month",
        )
        birthday = parser.add_mutually_exclusive_group()
        birthday.add_argument(
            "--birthday",
            dest="birthday",
            required=False,
            help="The person's birthday",
        )
        birthday.add_argument(
            "--clear-birthday",
            dest="clear_birthday",
            required=False,
            action="store_const",
            const=True,
            default=False,
            help="Clear the birthday",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(args.name)
        else:
            name = UpdateAction.do_nothing()
        if args.relationship:
            relationship = UpdateAction.change_to(
                PersonRelationship.from_raw(args.relationship),
            )
        else:
            relationship = UpdateAction.do_nothing()
        catch_up_period: UpdateAction[Optional[RecurringTaskPeriod]]
        if args.clear_catch_up_period:
            catch_up_period = UpdateAction.change_to(None)
        elif args.catch_up_period is not None:
            catch_up_period = UpdateAction.change_to(
                RecurringTaskPeriod.from_raw(args.catch_up_period),
            )
        else:
            catch_up_period = UpdateAction.do_nothing()
        catch_up_eisen: UpdateAction[Optional[Eisen]]
        if args.clear_catch_up_eisen:
            catch_up_eisen = UpdateAction.change_to(None)
        elif args.catch_up_eisen:
            catch_up_eisen = UpdateAction.change_to(Eisen.from_raw(args.eisen))
        else:
            catch_up_eisen = UpdateAction.do_nothing()
        catch_up_difficulty: UpdateAction[Optional[Difficulty]]
        if args.clear_catch_up_difficulty:
            catch_up_difficulty = UpdateAction.change_to(None)
        elif args.catch_up_difficulty is not None:
            catch_up_difficulty = UpdateAction.change_to(
                Difficulty.from_raw(args.catch_up_difficulty),
            )
        else:
            catch_up_difficulty = UpdateAction.do_nothing()
        catch_up_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_catch_up_actionable_from_day:
            catch_up_actionable_from_day = UpdateAction.change_to(None)
        elif args.catch_up_actionable_from_day is not None:
            catch_up_actionable_from_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.catch_up_actionable_from_day,
                ),
            )
        else:
            catch_up_actionable_from_day = UpdateAction.do_nothing()
        catch_up_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_catch_up_actionable_from_month:
            catch_up_actionable_from_month = UpdateAction.change_to(None)
        elif args.catch_up_actionable_from_month is not None:
            catch_up_actionable_from_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.catch_up_actionable_from_month,
                ),
            )
        else:
            catch_up_actionable_from_month = UpdateAction.do_nothing()
        catch_up_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        if args.clear_catch_up_due_at_time:
            catch_up_due_at_time = UpdateAction.change_to(None)
        elif args.catch_up_due_at_time is not None:
            catch_up_due_at_time = UpdateAction.change_to(
                RecurringTaskDueAtTime.from_raw(args.catch_up_due_at_time),
            )
        else:
            catch_up_due_at_time = UpdateAction.do_nothing()
        catch_up_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_catch_up_due_at_day:
            catch_up_due_at_day = UpdateAction.change_to(None)
        elif args.catch_up_due_at_day is not None:
            catch_up_due_at_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.catch_up_due_at_day,
                ),
            )
        else:
            catch_up_due_at_day = UpdateAction.do_nothing()
        catch_up_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_catch_up_due_at_month:
            catch_up_due_at_month = UpdateAction.change_to(None)
        elif args.catch_up_due_at_month is not None:
            catch_up_due_at_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.catch_up_due_at_month,
                ),
            )
        else:
            catch_up_due_at_month = UpdateAction.do_nothing()
        birthday: UpdateAction[Optional[PersonBirthday]]
        if args.clear_birthday:
            birthday = UpdateAction.change_to(None)
        elif args.birthday is not None:
            birthday = UpdateAction.change_to(PersonBirthday.from_raw(args.birthday))
        else:
            birthday = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            PersonUpdateArgs(
                ref_id=ref_id,
                name=name,
                relationship=relationship,
                catch_up_period=catch_up_period,
                catch_up_eisen=catch_up_eisen,
                catch_up_difficulty=catch_up_difficulty,
                catch_up_actionable_from_day=catch_up_actionable_from_day,
                catch_up_actionable_from_month=catch_up_actionable_from_month,
                catch_up_due_at_time=catch_up_due_at_time,
                catch_up_due_at_day=catch_up_due_at_day,
                catch_up_due_at_month=catch_up_due_at_month,
                birthday=birthday,
            ),
        )
