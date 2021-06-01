"""Command for showing the vacations."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.vacations.commands.vacation_find import VacationFindCommand
from models.basic import BasicValidator
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class VacationsShow(command.Command):
    """Command class for showing the vacations."""

    _basic_validator: Final[BasicValidator]
    _command: Final[VacationFindCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: VacationFindCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of vacations"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--show-archived", dest="show_archived", default=False, action="store_true",
                            help="Whether to show archived vacations or not")
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=False, help="Show only tasks selected by this id")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        response = self._command.execute(VacationFindCommand.Args(
            allow_archived=show_archived, filter_ref_ids=ref_ids if len(ref_ids) > 0 else None))
        for vacation in response.vacations:
            print(f'id={vacation.ref_id} {vacation.name} ' +
                  f'start={self._basic_validator.adate_to_user(vacation.start_date)} ' +
                  f'end={self._basic_validator.adate_to_user(vacation.end_date)} ' +
                  f'{"archived=" + str(vacation.archived) if show_archived else ""}')
