"""Command for showing metrics."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final, cast

import command.command as command
from domain.adate import ADate
from domain.metrics.metric_key import MetricKey
from use_cases.metrics.find import MetricFindCommand
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class MetricShow(command.Command):
    """Command for showing metrics."""

    _global_properties: Final[GlobalProperties]
    _command: Final[MetricFindCommand]

    def __init__(self, global_properties: GlobalProperties, the_command: MetricFindCommand) -> None:
        """Constructor."""
        self._global_properties = global_properties
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
        metric_keys = [MetricKey.from_raw(mk) for mk in args.metric_keys] \
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
                      (f" {ADate.to_user_str(self._global_properties.timezone, metric_entry.collection_time)}") +
                      f" val={metric_entry.value}")

            if metric_response_entry.metric_collection_inbox_tasks:
                print(f"  Collection Tasks:")
                for inbox_task in sorted(
                        metric_response_entry.metric_collection_inbox_tasks,
                        key=lambda it: cast(ADate, it.due_date)):
                    print(f"    -id={inbox_task.ref_id} {inbox_task.name} {inbox_task.status.for_notion()}")
