"""UseCase for hard removing a smart list."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.use_cases.smart_lists.remove import SmartListRemoveUseCase


class SmartListsRemove(command.Command):
    """UseCase for hard removing of a smart list."""

    _command: Final[SmartListRemoveUseCase]

    def __init__(self, the_command: SmartListRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list",
            dest="smart_list_key",
            required=True,
            help="The key of the smart list to remove",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = SmartListKey.from_raw(args.smart_list_key)

        self._command.execute(
            progress_reporter, SmartListRemoveUseCase.Args(key=smart_list_key)
        )
