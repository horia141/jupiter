"""Command for showing metrics."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import pendulum

import command.command as command
from domain.metrics.commands.metric_find import MetricFindCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class MetricShow(command.Command):
    """Command for showing metrics."""

    _basic_validator: Final[BasicValidator]
    _command: Final[MetricFindCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricFindCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-show"

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
        response = self._command.execute(MetricFindCommand.Args(allow_archived=False, filter_keys=metric_keys))

        for metric_response_entry in response.metrics:
            metric = metric_response_entry.metric
            collection_project = metric_response_entry.collection_project
            metric_entries = metric_response_entry.metric_entries

            print(f"{metric.key}: {metric.name}" +
                  (f" @{metric.collection_params.period.for_notion()} in " +
                   (f"{collection_project.name if collection_project else 'Default'}") +
                   (f" eisen={','.join(e.for_notion() for e in metric.collection_params.eisen)}"
                    if metric.collection_params.eisen else '')) +
                  (f" difficulty={metric.collection_params.difficulty.for_notion()}"
                   if metric.collection_params.difficulty else '') +
                  (f" actionable-from-day={metric.collection_params.actionable_from_day}"
                   if metric.collection_params.actionable_from_day else '') +
                  (f" actionable-from-month={metric.collection_params.actionable_from_month}"
                   if metric.collection_params.actionable_from_month else '') +
                  (f" due-at-time={metric.collection_params.due_at_time}"
                   if metric.collection_params.due_at_time else '') +
                  (f" due-at-day={metric.collection_params.due_at_day}"
                   if metric.collection_params.due_at_day else '') +
                  (f" due-at-month={metric.collection_params.due_at_month}"
                   if metric.collection_params.due_at_month else '')
                  if metric.collection_params else '' +
                  (f' #{metric.metric_unit.for_notion()}' if metric.metric_unit else ''))

            for metric_entry in sorted(metric_entries, key=lambda me: me.collection_time):
                print(f"  - id={metric_entry.ref_id}" +
                      (f" {metric_entry.collection_time.to_date_string()}"
                       if isinstance(metric_entry.collection_time, pendulum.Date)
                       else f" {metric_entry.collection_time.to_datetime_string()}") +
                      f" val={metric_entry.value}")

            if metric_response_entry.metric_collection_inbox_tasks:
                print(f"  Collection Tasks:")
                for inbox_task in sorted(
                        metric_response_entry.metric_collection_inbox_tasks, key=lambda it: it.due_date):
                    print(f"    -id={inbox_task.ref_id} {inbox_task.name} {inbox_task.status.for_notion()}")
