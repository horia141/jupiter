"""Command for updating a metric's properties."""
from argparse import Namespace, ArgumentParser
from typing import Final, Optional

import command.command as command
from domain.metrics.commands.metric_update import MetricUpdateCommand
from models.basic import BasicValidator, RecurringTaskPeriod
from models.framework import UpdateAction


class MetricUpdate(command.Command):
    """Command for updating a metric's properties."""

    _basic_validator: Final[BasicValidator]
    _command: Final[MetricUpdateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricUpdateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")
        parser.add_argument("--name", dest="name", required=False, help="The name of the metric")
        parser.add_argument("--collection-period", dest="collection_period", required=False,
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period at which a metric should be recorded")
        parser.add_argument("--clear-collection-period", dest="clear_collection_period", default=False,
                            action="store_const", const=True, help="Clear the collection period")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = self._basic_validator.metric_key_validate_and_clean(args.metric_key)
        if args.name is not None:
            name = UpdateAction.change_to(self._basic_validator.entity_name_validate_and_clean(args.name))
        else:
            name = UpdateAction.do_nothing()
        collection_period: UpdateAction[Optional[RecurringTaskPeriod]]
        if args.clear_collection_period:
            collection_period = UpdateAction.change_to(None)
        elif args.collection_period is not None:
            collection_period = UpdateAction.change_to(
                self._basic_validator.recurring_task_period_validate_and_clean(args.collection_period))
        else:
            collection_period = UpdateAction.do_nothing()
        self._command.execute(MetricUpdateCommand.Args(
            key=metric_key, name=name, collection_period=collection_period))
