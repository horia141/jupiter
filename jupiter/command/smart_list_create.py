"""UseCase for creating a smart list."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.use_cases.smart_lists.create import SmartListCreateUseCase


class SmartListCreate(command.Command):
    """UseCase for creating a smart list."""

    _command: Final[SmartListCreateUseCase]

    def __init__(self, the_command: SmartListCreateUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list",
            dest="smart_list_key",
            required=True,
            help="The key of the smart list",
        )
        parser.add_argument(
            "--name", dest="name", required=True, help="The name of the smart list"
        )
        parser.add_argument(
            "--icon",
            dest="icon",
            required=False,
            help="A unicode icon or :alias: for the smart list",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = SmartListKey.from_raw(args.smart_list_key)
        name = SmartListName.from_raw(args.name)
        icon = EntityIcon.from_raw(args.icon) if args.icon else None

        self._command.execute(
            progress_reporter,
            SmartListCreateUseCase.Args(key=smart_list_key, name=name, icon=icon),
        )
