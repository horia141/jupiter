"""Command for updating a vacation's properties."""
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.common.adate import ADate
from domain.common.entity_name import EntityName
from domain.vacations.commands.vacation_update import VacationUpdateCommand
from models.framework import UpdateAction, EntityId
from utils.global_properties import GlobalProperties


class VacationUpdate(command.Command):
    """Command for updating a vacation's properties."""

    _global_properties: Final[GlobalProperties]
    _command: Final[VacationUpdateCommand]

    def __init__(self, global_properties: GlobalProperties, the_command: VacationUpdateCommand) -> None:
        """Constructor."""
        self._global_properties = global_properties
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
            name = UpdateAction.change_to(EntityName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.start_date is not None:
            start_date = UpdateAction.change_to(ADate.from_raw(self._global_properties.timezone, args.start_date))
        else:
            start_date = UpdateAction.do_nothing()
        if args.end_date is not None:
            end_date = UpdateAction.change_to(ADate.from_raw(self._global_properties.timezone, args.end_date))
        else:
            end_date = UpdateAction.do_nothing()
        self._command.execute(VacationUpdateCommand.Args(
            ref_id=ref_id, name=name, start_date=start_date, end_date=end_date))
