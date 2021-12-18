"""Command for associating an inbox task with a big plan."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from models.framework import EntityId
from use_cases.inbox_tasks.associate_with_big_plan import InboxTaskAssociateWithBigPlanCommand

LOGGER = logging.getLogger(__name__)


class InboxTaskAssociateWithBigPlan(command.Command):
    """Command class for associating an inbox task with a big plan."""

    _command: Final[InboxTaskAssociateWithBigPlanCommand]

    def __init__(self, the_command: InboxTaskAssociateWithBigPlanCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-task-associate-with-big-plan"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Associate an inbox task with a big plan"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")
        parser.add_argument("--big-plan-id", type=str, dest="big_plan_ref_id",
                            help="The id of a big plan to associate this task to.")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        big_plan_ref_id = EntityId.from_raw(args.big_plan_ref_id)\
            if args.big_plan_ref_id else None
        self._command.execute(InboxTaskAssociateWithBigPlanCommand.Args(ref_id, big_plan_ref_id))
