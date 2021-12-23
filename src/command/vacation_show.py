"""UseCase for showing the vacations."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.adate import ADate
from use_cases.vacations.find import VacationFindUseCase
from framework.base.entity_id import EntityId
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class VacationsShow(command.Command):
    """UseCase class for showing the vacations."""

    _global_properties: Final[GlobalProperties]
    _command: Final[VacationFindUseCase]

    def __init__(self, global_properties: GlobalProperties, the_command: VacationFindUseCase) -> None:
        """Constructor."""
        self._global_properties = global_properties
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
        response = self._command.execute(VacationFindUseCase.Args(
            allow_archived=show_archived, filter_ref_ids=ref_ids if len(ref_ids) > 0 else None))
        for vacation in response.vacations:
            print(f'id={vacation.ref_id} {vacation.name} ' +
                  f'start={ADate.to_user_str(self._global_properties.timezone, vacation.start_date)} ' +
                  f'end={ADate.to_user_str(self._global_properties.timezone, vacation.end_date)} ' +
                  f'{"archived=" + str(vacation.archived) if show_archived else ""}')
