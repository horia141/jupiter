"""UseCase for hard removing a metric entry."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import jupiter.command.command as command
from jupiter.use_cases.metrics.entry.remove import MetricEntryRemoveUseCase
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


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
        parser.add_argument("--id", dest="ref_ids", required=True, default=[], action="append",
                            help="The ids of the metric entries")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._the_command.execute(ref_id)
