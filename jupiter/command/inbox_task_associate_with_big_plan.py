"""UseCase for associating an inbox task with a big plan."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.inbox_tasks.associate_with_big_plan import InboxTaskAssociateWithBigPlanUseCase

LOGGER = logging.getLogger(__name__)


class InboxTaskAssociateWithBigPlan(command.Command):
    """UseCase class for associating an inbox task with a big plan."""

    _command: Final[InboxTaskAssociateWithBigPlanUseCase]

    def __init__(self, the_command: InboxTaskAssociateWithBigPlanUseCase) -> None:
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
        big_plan = parser.add_mutually_exclusive_group()
        big_plan.add_argument(
            "--big-plan-id", type=str, dest="big_plan_ref_id", help="The id of a big plan to associate this task to.")
        big_plan.add_argument(
            "--clear-big-plan", dest="clear_big_plan", default=False, action="store_const", const=True,
            help="Clear the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.clear_big_plan:
            big_plan_ref_id = None
        else:
            big_plan_ref_id = EntityId.from_raw(args.big_plan_ref_id)
        self._command.execute(InboxTaskAssociateWithBigPlanUseCase.Args(ref_id=ref_id, big_plan_ref_id=big_plan_ref_id))
