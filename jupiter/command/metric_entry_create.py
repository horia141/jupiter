"""UseCase for creating a metric entry."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import jupiter.command.command as command
from jupiter.domain.adate import ADate
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.use_cases.metrics.entry.create import MetricEntryCreateUseCase

LOGGER = logging.getLogger(__name__)


class MetricEntryCreate(command.Command):
    """UseCase for creating a metric entry."""

    _command: Final[MetricEntryCreateUseCase]

    def __init__(self, the_command: MetricEntryCreateUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-entry-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")
        parser.add_argument("--collection-time", dest="collection_time", required=False,
                            help="The time at which a metric should be recorded")
        parser.add_argument("--value", dest="value", required=True, type=float,
                            help="The value for the metric")
        parser.add_argument("--notes", dest="notes", required=False, type=str,
                            help="A note for the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = MetricKey.from_raw(args.metric_key)
        collection_time = ADate.from_str(args.collection_time) \
            if args.collection_time else None
        value = args.value
        notes = args.notes
        self._command.execute(MetricEntryCreateUseCase.Args(
            metric_key=metric_key, collection_time=collection_time, value=value, notes=notes))
