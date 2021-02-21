"""Command for removing a metric."""
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.metrics.commands.metric_remove import MetricRemoveCommand
from models.basic import BasicValidator


class MetricRemove(command.Command):
    """Command for hard removing a metric."""

    _basic_validator: Final[BasicValidator]
    _command: Final[MetricRemoveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricRemoveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_keys", required=True, default=[], action="append",
                            help="The key of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_keys = [self._basic_validator.metric_key_validate_and_clean(mk) for mk in args.metric_keys]
        for key in metric_keys:
            self._command.execute(key)
