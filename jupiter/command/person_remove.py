"""UseCase for removing a person."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.persons.remove import PersonRemoveUseCase


class PersonRemove(command.Command):
    """UseCase for removing a person."""

    _command: Final[PersonRemoveUseCase]

    def __init__(self, the_command: PersonRemoveUseCase) -> None:
        """Constructor."""
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
        parser.add_argument(
            "--id", dest="ref_id", required=True, help="The id of the person"
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(
            progress_reporter, PersonRemoveUseCase.Args(ref_id=ref_id)
        )
