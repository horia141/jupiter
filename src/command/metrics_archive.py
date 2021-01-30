"""Command for archiving a metric."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.metrics import MetricsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricsArchive(command.Command):
    """Command for creating a metric."""

    _basic_validator: Final[BasicValidator]
    _metrics_controller: Final[MetricsController]

    def __init__(self, basic_validator: BasicValidator, metrics_controller: MetricsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._metrics_controller = metrics_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metrics-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = self._basic_validator.metric_key_validate_and_clean(args.metric_key)
        self._metrics_controller.archive_metric(key=metric_key)
