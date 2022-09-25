"""UseCase for archiving a smart list."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.use_cases.smart_lists.archive import SmartListArchiveUseCase


class SmartListArchive(command.Command):
    """UseCase for archiving of a smart list."""

    _command: Final[SmartListArchiveUseCase]

    def __init__(self, the_command: SmartListArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list",
            dest="smart_list_key",
            required=True,
            help="The key of the smart list to archive",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = SmartListKey.from_raw(args.smart_list_key)

        self._command.execute(
            progress_reporter, SmartListArchiveUseCase.Args(key=smart_list_key)
        )
