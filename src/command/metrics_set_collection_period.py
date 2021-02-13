"""Command for setting the collection period of a metric."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.metrics import MetricsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricsSetCollectionPeriod(command.Command):
    """Command for setting the collection period of a metric."""

    _basic_validator: Final[BasicValidator]
    _metrics_controller: Final[MetricsController]

    def __init__(self, basic_validator: BasicValidator, metrics_controller: MetricsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._metrics_controller = metrics_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metrics-set-collection-period"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the collection period of a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")
        parser.add_argument("--collection-period", dest="collection_period", required=False,
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period at which a metric should be recorded")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = self._basic_validator.metric_key_validate_and_clean(args.metric_key)
        collection_period = self._basic_validator.recurring_task_period_validate_and_clean(args.collection_period) \
            if args.collection_period else None
        self._metrics_controller.set_metric_collection_period(key=metric_key, collection_period=collection_period)
