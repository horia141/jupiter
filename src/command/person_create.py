"""Command for adding a person."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.common.difficulty import Difficulty
from domain.common.eisen import Eisen
from domain.common.entity_name import EntityName
from domain.common.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.common.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.common.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.common.recurring_task_period import RecurringTaskPeriod
from domain.prm.commands.person_create import PersonCreateCommand
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship

LOGGER = logging.getLogger(__name__)


class PersonCreate(command.Command):
    """Command class for adding a person."""

    _command: Final[PersonCreateCommand]

    def __init__(self, the_command: PersonCreateCommand):
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "person-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Add a new person"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", dest="name", required=True, help="The name of the person")
        parser.add_argument("--relationship", dest="relationship", required=True,
                            choices=PersonRelationship.all_values(), help="The person's relationship to you")
        parser.add_argument("--catch-up-period", dest="catch_up_period", required=False,
                            choices=RecurringTaskPeriod.all_values(),
                            help="The period at which a metric should be recorded")
        parser.add_argument("--catch-up-eisen", dest="catch_up_eisen", default=[], action="append",
                            choices=Eisen.all_values(),
                            help="The Eisenhower matrix values to use for catch up tasks")
        parser.add_argument("--catch-up-difficuslty", dest="catch_up_difficulty",
                            choices=Difficulty.all_values(),
                            help="The difficulty to use for catch up tasks")
        parser.add_argument("--catch-up-actionable-from-day", type=int,
                            dest="catch_up_actionable_from_day", metavar="DAY",
                            help="The day of the interval the catch up task will be actionable from")
        parser.add_argument("--catch-up-actionable-from-month", type=int,
                            dest="catch_up_actionable_from_month", metavar="MONTH",
                            help="The month of the interval the catch up task will be actionable from")
        parser.add_argument("--catch-up-due-at-time", dest="catch_up_due_at_time",
                            metavar="HH:MM", help="The time a task will be due on")
        parser.add_argument("--catch-up-due-at-day", type=int, dest="catch_up_due_at_day", metavar="DAY",
                            help="The day of the interval the catch up task will be due on")
        parser.add_argument("--catch-up-due-at-month", type=int, dest="catch_up_due_at_month", metavar="MONTH",
                            help="The month of the interval the catch up task will be due on")
        parser.add_argument("--birthday", dest="birthday", required=False,
                            help="The person's birthday")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        name = EntityName.from_raw(args.name)
        relationship = PersonRelationship.from_raw(args.relationship)
        catch_up_period = RecurringTaskPeriod.from_raw(args.catch_up_period) \
            if args.catch_up_period else None
        catch_up_eisen = [Eisen.from_raw(e) for e in args.catch_up_eisen]
        catch_up_difficulty = Difficulty.from_raw(args.catch_up_difficulty) \
            if args.catch_up_difficulty else None
        catch_up_actionable_from_day = \
            RecurringTaskDueAtDay.from_raw(catch_up_period, args.catch_up_actionable_from_day) \
            if args.actionable_from_day and catch_up_period else None
        catch_up_actionable_from_month = \
            RecurringTaskDueAtMonth.from_raw(catch_up_period, args.catch_up_actionable_from_month) \
            if args.catch_up_actionable_from_month and catch_up_period else None
        catch_up_due_at_time = \
            RecurringTaskDueAtTime.from_raw(args.catch_up_due_at_time) \
                if args.catch_up_due_at_time and catch_up_period else None
        catch_up_due_at_day = RecurringTaskDueAtDay.from_raw(catch_up_period, args.catch_up_due_at_day) \
                if args.catch_up_due_at_day and catch_up_period else None
        catch_up_due_at_month = \
            RecurringTaskDueAtMonth.from_raw(catch_up_period, args.catch_up_due_at_month) \
                if args.catch_up_due_at_month and catch_up_period else None
        birthday = PersonBirthday.from_raw(args.birthday) if args.birthday else None

        self._command.execute(PersonCreateCommand.Args(
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
            birthday=birthday))
