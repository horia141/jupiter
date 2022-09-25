"""UseCase for hard removing a metric entry."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.metrics.entry.remove import MetricEntryRemoveUseCase


class MetricEntryRemove(command.Command):
    """UseCase for hard removing a metric."""

    _the_command: Final[MetricEntryRemoveUseCase]

    def __init__(self, the_command: MetricEntryRemoveUseCase) -> None:
        """Constructor."""
        self._the_command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-entry-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the metric entry",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._the_command.execute(
            progress_reporter, MetricEntryRemoveUseCase.Args(ref_id=ref_id)
        )
