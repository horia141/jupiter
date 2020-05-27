"""Command for syncing the recurring tasks from Notion."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from models.basic import BasicValidator, SyncPrefer

LOGGER = logging.getLogger(__name__)


class RecurringTasksSync(command.Command):
    """Command class for syncing  projects."""

    _basic_validator: Final[BasicValidator]
    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, basic_validator: BasicValidator, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-sync"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Synchronises Notion and the local storage for recurring tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True,
                            help="Allow only tasks from this project")
        parser.add_argument("--prefer", dest="sync_prefer", choices=BasicValidator.sync_prefer_values(),
                            default=SyncPrefer.NOTION.value, help="Which source to prefer")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = self._basic_validator.project_key_validate_and_clean(args.project_key)
        sync_prefer = self._basic_validator.sync_prefer_validate_and_clean(args.sync_prefer)
        self._recurring_tasks_controller.recurring_tasks_sync(project_key, sync_prefer)
