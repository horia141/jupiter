"""UseCase for creating a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.use_cases.smart_lists.tag.create import SmartListTagCreateUseCase
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName

LOGGER = logging.getLogger(__name__)


class SmartListTagCreate(command.Command):
    """UseCase for creating a smart list tag."""

    _command: Final[SmartListTagCreateUseCase]

    def __init__(self, the_command: SmartListTagCreateUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-tag-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list",
            dest="smart_list_key",
            required=True,
            help="The key of the smart list to add the tag to",
        )
        parser.add_argument(
            "--name", dest="name", required=True, help="The name of the smart list"
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = SmartListKey.from_raw(args.smart_list_key)
        tag_name = SmartListTagName.from_raw(args.name)
        self._command.execute(
            SmartListTagCreateUseCase.Args(
                smart_list_key=smart_list_key, tag_name=tag_name
            )
        )
