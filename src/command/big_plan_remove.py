"""UseCase for hard remove big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from framework.entity_id import EntityId
from use_cases.big_plans.remove import BigPlanRemoveUseCase


class BigPlanRemove(command.Command):
    """UseCase class for hard removing big plans."""

    _command: Final[BigPlanRemoveUseCase]

    def __init__(self, the_command: BigPlanRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plan-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove big plans"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id",
                            required=True, help="Show only tasks selected by this id")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(BigPlanRemoveUseCase.Args(ref_id))
