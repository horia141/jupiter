"""UseCase for archiving a metric."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.use_cases.metrics.archive import MetricArchiveUseCase
from jupiter.domain.metrics.metric_key import MetricKey


class MetricArchive(command.Command):
    """UseCase for creating a metric."""

    _command: Final[MetricArchiveUseCase]

    def __init__(self, the_command: MetricArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = MetricKey.from_raw(args.metric_key)
        self._command.execute(MetricArchiveUseCase.Args(key=metric_key))
