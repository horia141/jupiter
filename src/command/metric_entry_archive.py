"""Command for archiving a metric entry."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.metrics.commands.metric_entry_archive import MetricEntryArchiveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricEntryArchive(command.Command):
    """Command for archiving a metric entry."""

    _basic_validator: Final[BasicValidator]
    _command: Final[MetricEntryArchiveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricEntryArchiveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-entry-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True, help="The id of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        self._command.execute(ref_id)
