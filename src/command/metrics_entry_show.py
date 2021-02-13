"""Command for showing metric entries."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import pendulum

import command.command as command
from controllers.metrics import MetricsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricsEntryShow(command.Command):
    """Command for showing metric entries."""

    _basic_validator: Final[BasicValidator]
    _metrics_controller: Final[MetricsController]

    def __init__(self, basic_validator: BasicValidator, metrics_controller: MetricsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._metrics_controller = metrics_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metrics-entry-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the metrics entries"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_ids", required=False, default=[], action="append",
                            help="The ids of the metric entries to show")
        parser.add_argument("--metric", dest="metric_keys", required=False, default=[], action="append",
                            help="The key of the metrics to show")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        metric_keys = [self._basic_validator.metric_key_validate_and_clean(mk) for mk in args.metric_keys] \
            if len(args.metric_keys) > 0 else None
        response = self._metrics_controller.load_all_metric_entries(
            filter_ref_ids=ref_ids, filter_metric_keys=metric_keys)

        for metric_response_entry in response.metric_entries:
            metric = metric_response_entry.metric
            metric_entry = metric_response_entry.metric_entry

            print(f"id={metric_entry.ref_id}" +
                  (f" {metric_entry.collection_time.to_date_string()}"
                   if isinstance(metric_entry.collection_time, pendulum.Date)
                   else f" {metric_entry.collection_time.to_datetime_string()}") +
                  f" val={metric_entry.value}" +
                  f" in {metric.key}:{metric.name}")
