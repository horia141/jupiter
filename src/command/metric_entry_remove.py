"""Command for hard removing a metric entry."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.metrics.commands.metric_entry_remove import MetricEntryRemoveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricEntryRemove(command.Command):
    """Command for hard removing a metric."""

    _basic_validator: Final[BasicValidator]
    _the_command: Final[MetricEntryRemoveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricEntryRemoveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
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
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._the_command.execute(ref_id)
