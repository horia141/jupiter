"""Command for updating a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_tag_update import SmartListTagUpdateCommand
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from models.framework import UpdateAction, EntityId

LOGGER = logging.getLogger(__name__)


class SmartListTagUpdate(command.Command):
    """Command for creating a smart list tag."""

    _command: Final[SmartListTagUpdateCommand]

    def __init__(self, the_command: SmartListTagUpdateCommand) -> None:
        """Constructor."""
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
        parser.add_argument("--name", dest="tag_name", required=False, help="The name of the smart list")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.tag_name:
            tag_name = UpdateAction.change_to(SmartListTagName.from_raw(args.tag_name))
        else:
            tag_name = UpdateAction.do_nothing()
        self._command.execute(SmartListTagUpdateCommand.Args(ref_id=ref_id, tag_name=tag_name))
