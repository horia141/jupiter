"""Command for setting the notes of a metric entry."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.metrics import MetricsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricsEntrySetNotes(command.Command):
    """Command for setting the notes of a metric entry."""

    _basic_validator: Final[BasicValidator]
    _metrics_controller: Final[MetricsController]

    def __init__(self, basic_validator: BasicValidator, metrics_controller: MetricsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._metrics_controller = metrics_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metrics-entry-set-notes"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the notes of a metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True, help="The id of the metric entry")
        parser.add_argument("--notes", dest="notes", required=False, type=str,
                            help="A note for the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        notes = args.notes
        self._metrics_controller.set_metric_entry_notes(ref_id, notes)
