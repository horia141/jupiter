"""Command for archiving a metric."""
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.metrics.commands.metric_archive import MetricArchiveCommand
from models.basic import BasicValidator


class MetricArchive(command.Command):
    """Command for creating a metric."""

    _basic_validator: Final[BasicValidator]
    _command: Final[MetricArchiveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: MetricArchiveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-archive"

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
        self._command.execute(args=metric_key)
