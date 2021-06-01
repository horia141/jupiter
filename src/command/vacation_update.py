"""Command for updating a vacation's properties."""
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.vacations.commands.vacation_update import VacationUpdateCommand
from models.basic import BasicValidator
from models.framework import UpdateAction, EntityId


class VacationUpdate(command.Command):
    """Command for updating a vacation's properties."""

    _basic_validator: Final[BasicValidator]
    _command: Final[VacationUpdateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: VacationUpdateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacation to modify")
        parser.add_argument("--name", dest="name", required=False, help="The name of the vacation")
        parser.add_argument("--start-date", dest="start_date", required=False, help="The vacation start date")
        parser.add_argument("--end-date", dest="end_date", required=False, help="The vacation end date")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name is not None:
            name = UpdateAction.change_to(self._basic_validator.entity_name_validate_and_clean(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.start_date is not None:
            start_date = UpdateAction.change_to(self._basic_validator.adate_validate_and_clean(args.start_date))
        else:
            start_date = UpdateAction.do_nothing()
        if args.end_date is not None:
            end_date = UpdateAction.change_to(self._basic_validator.adate_validate_and_clean(args.end_date))
        else:
            end_date = UpdateAction.do_nothing()
        self._command.execute(VacationUpdateCommand.Args(
            ref_id=ref_id, name=name, start_date=start_date, end_date=end_date))
