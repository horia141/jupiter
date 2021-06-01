"""Command for updating a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_tag_update import SmartListTagUpdateCommand
from models.basic import BasicValidator
from models.framework import UpdateAction, EntityId

LOGGER = logging.getLogger(__name__)


class SmartListTagUpdate(command.Command):
    """Command for creating a smart list tag."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListTagUpdateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListTagUpdateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-tag-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True, help="The id of the smart list tag")
        parser.add_argument("--name", dest="name", required=False, help="The name of the smart list")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(self._basic_validator.tag_validate_and_clean(args.name))
        else:
            name = UpdateAction.do_nothing()
        self._command.execute(SmartListTagUpdateCommand.Args(ref_id=ref_id, name=name))
