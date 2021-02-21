"""Command for creating a metric."""
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.metrics.commands.metric_create import MetricCreateCommand
from models.basic import BasicValidator


class MetricCreate(command.Command):
    """Command for creating a metric."""

    _basic_validator: Final[BasicValidator]
    _command: Final[MetricCreateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricCreateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")
        parser.add_argument("--name", dest="name", required=True, help="The name of the metric")
        parser.add_argument("--collection-period", dest="collection_period", required=False,
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period at which a metric should be recorded")
        parser.add_argument("--unit", dest="metric_unit", required=False,
                            choices=BasicValidator.metric_unit_values(),
                            help="The unit for the values of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = self._basic_validator.metric_key_validate_and_clean(args.metric_key)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        collection_period = self._basic_validator.recurring_task_period_validate_and_clean(args.collection_period)\
            if args.collection_period else None
        metric_unit = self._basic_validator.metric_unit_validate_and_clean(args.metric_unit)\
            if args.metric_unit else None
        self._command.execute(MetricCreateCommand.Args(
            key=metric_key, name=name, collection_period=collection_period, metric_unit=metric_unit))
