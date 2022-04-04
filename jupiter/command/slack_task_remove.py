"""UseCase for hard remove slack tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.push_integrations.slack.remove import SlackTaskRemoveUseCase


class SlackTaskRemove(command.Command):
    """UseCase class for hard removing slack tasks."""

    _command: Final[SlackTaskRemoveUseCase]

    def __init__(self, the_command: SlackTaskRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "slack-task-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove slack tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="Show only tasks selected by this id",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(SlackTaskRemoveUseCase.Args(ref_id))
