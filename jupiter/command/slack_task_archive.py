"""UseCase for archiving a slack task."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.push_integrations.slack.archive import SlackTaskArchiveUseCase


class SlackTaskArchive(command.Command):
    """UseCase class for archiving a slack task."""

    _command: Final[SlackTaskArchiveUseCase]

    def __init__(self, the_command: SlackTaskArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "slack-task-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a slack task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the slack task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(SlackTaskArchiveUseCase.Args(ref_id))
