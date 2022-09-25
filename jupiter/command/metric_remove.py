"""UseCase for removing a metric."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.use_cases.metrics.remove import MetricRemoveUseCase


class MetricRemove(command.Command):
    """UseCase for hard removing a metric."""

    _command: Final[MetricRemoveUseCase]

    def __init__(self, the_command: MetricRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--metric", dest="metric_key", required=True, help="The key of the metric"
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = MetricKey.from_raw(args.metric_key)

        self._command.execute(
            progress_reporter, MetricRemoveUseCase.Args(key=metric_key)
        )
