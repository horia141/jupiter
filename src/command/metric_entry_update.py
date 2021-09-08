"""Command for updating a metric entry's properties."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final, Optional

import command.command as command
from domain.common.adate import ADate
from domain.metrics.commands.metric_entry_update import MetricEntryUpdateCommand
from models.framework import UpdateAction, EntityId

LOGGER = logging.getLogger(__name__)


class MetricEntryUpdate(command.Command):
    """Command for updating a metric entry's properties."""

    _command: Final[MetricEntryUpdateCommand]

    def __init__(self, the_command: MetricEntryUpdateCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-entry-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True, help="The id of the metric")
        parser.add_argument("--collection-time", dest="collection_time", required=False,
                            help="The time at which a metric should be recorded")
        parser.add_argument("--value", dest="value", required=False, type=float,
                            help="The value for the metric")
        parser.add_argument("--notes", dest="notes", required=False, type=str,
                            help="A note for the metric")
        parser.add_argument("--clear-notes", dest="clear_notes", default=False,
                            action="store_const", const=True, help="Clear the notes")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        collection_time = UpdateAction.change_to(ADate.from_str(args.collection_time)) \
            if args.collection_time is not None else UpdateAction.do_nothing()
        value = UpdateAction.change_to(args.value) if args.value is not None else UpdateAction.do_nothing()
        notes: UpdateAction[Optional[str]]
        if args.clear_notes:
            notes = UpdateAction.change_to(None)
        elif args.notes is not None:
            notes = UpdateAction.change_to(args.notes)
        else:
            notes = UpdateAction.do_nothing()
        self._command.execute(MetricEntryUpdateCommand.Args(
            ref_id=ref_id, collection_time=collection_time, value=value, notes=notes))
