"""Command for showing metrics."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import pendulum

import command.command as command
from controllers.metrics import MetricsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricsShow(command.Command):
    """Command for showing metrics."""

    _basic_validator: Final[BasicValidator]
    _metrics_controller: Final[MetricsController]

    def __init__(self, basic_validator: BasicValidator, metrics_controller: MetricsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._metrics_controller = metrics_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metrics-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the metrics"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_keys", required=False, default=[], action="append",
                            help="The key of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_keys = [self._basic_validator.metric_key_validate_and_clean(mk) for mk in args.metric_keys] \
            if len(args.metric_keys) > 0 else None
        response = self._metrics_controller.load_all_metrics(filter_keys=metric_keys)

        for metric_response_entry in response.metrics:
            metric = metric_response_entry.metric
            metric_entries = metric_response_entry.metric_entries

            print(f"{metric.key}: {metric.name}" +
                  (f" @{metric.collection_period.for_notion()}" if metric.collection_period else '') +
                  (f' #{metric.metric_unit.for_notion()}' if metric.metric_unit else ''))

            for metric_entry in sorted(metric_entries, key=lambda me: me.collection_time):
                print(f"  - id={metric_entry.ref_id}" +
                      (f" {metric_entry.collection_time.to_date_string()}"
                       if isinstance(metric_entry.collection_time, pendulum.Date)
                       else f" {metric_entry.collection_time.to_datetime_string()}") +
                      f" val={metric_entry.value}")
