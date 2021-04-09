"""Command for adding a person."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.prm.commands.person_create import PersonCreateCommand
from domain.prm.person_birthday import PersonBirthday

from domain.prm.person_relationship import PersonRelationship
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class PersonCreate(command.Command):
    """Command class for adding a person."""

    _basic_validator: Final[BasicValidator]
    _command: Final[PersonCreateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: PersonCreateCommand):
        """Constructor."""
        self._basic_validator = basic_validator
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
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period at which a metric should be recorded")
        parser.add_argument("--catch-up-eisen", dest="catch_up_eisen", default=[], action="append",
                            choices=BasicValidator.eisen_values(),
                            help="The Eisenhower matrix values to use for catch up tasks")
        parser.add_argument("--catch-up-difficuslty", dest="catch_up_difficulty",
                            choices=BasicValidator.difficulty_values(),
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
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        relationship = PersonRelationship.from_raw(args.relationship)
        catch_up_period = self._basic_validator.recurring_task_period_validate_and_clean(args.catch_up_period) \
            if args.catch_up_period else None
        catch_up_eisen = [self._basic_validator.eisen_validate_and_clean(e) for e in args.catch_up_eisen]
        catch_up_difficulty = self._basic_validator.difficulty_validate_and_clean(args.catch_up_difficulty) \
            if args.catch_up_difficulty else None
        catch_up_actionable_from_day = self._basic_validator.recurring_task_due_at_day_validate_and_clean(
            catch_up_period, args.catch_up_actionable_from_day) \
            if args.actionable_from_day and catch_up_period else None
        catch_up_actionable_from_month = self._basic_validator.recurring_task_due_at_month_validate_and_clean(
            catch_up_period, args.catch_up_actionable_from_month) \
            if args.catch_up_actionable_from_month and catch_up_period else None
        catch_up_due_at_time = \
            self._basic_validator.recurring_task_due_at_time_validate_and_clean(args.catch_up_due_at_time) \
                if args.catch_up_due_at_time and catch_up_period else None
        catch_up_due_at_day = \
            self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                catch_up_period, args.catch_up_due_at_day) \
                if args.catch_up_due_at_day and catch_up_period else None
        catch_up_due_at_month = \
            self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                catch_up_period, args.catch_up_due_at_month) \
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
