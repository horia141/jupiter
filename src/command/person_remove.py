"""Command for removing a person."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.prm.commands.person_remove import PersonRemoveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class PersonRemove(command.Command):
    """Command for removing a person."""

    _basic_validator: Final[BasicValidator]
    _command: Final[PersonRemoveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: PersonRemoveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "person-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a person"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True, help="The id of the person")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        self._command.execute(ref_id)
