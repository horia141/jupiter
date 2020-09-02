"""Command for setting the Eisenhower status of an inbox task."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.basic import BasicValidator
LOGGER = logging.getLogger(__name__)


class InboxTasksSetEisen(command.Command):
    """Command class for setting the Eisenhower status of an inbox task."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-set-eisen"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Set the Eisenhower status an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            choices=BasicValidator.eisen_values(), help="The Eisenhower matrix values to use for task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        eisen = [self._basic_validator.eisen_validate_and_clean(e) for e in args.eisen]
        self._inbox_tasks_controller.set_inbox_task_eisen(ref_id, eisen)
