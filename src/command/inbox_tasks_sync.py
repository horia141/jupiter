"""Command for syncing the inbox tasks for a project."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.basic import BasicValidator, SyncPrefer

LOGGER = logging.getLogger(__name__)


class InboxTasksSync(command.Command):
    """Command class for syncing the inbox tasks for a project."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Sync the inbox tasks for a project between the local store and Notion"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True,
                            help="The key of the project")
        parser.add_argument("--prefer", dest="sync_prefer", choices=BasicValidator.sync_prefer_values(),
                            default=SyncPrefer.NOTION.value, help="Which source to prefer")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = self._basic_validator.project_key_validate_and_clean(args.project_key)
        sync_prefer = self._basic_validator.sync_prefer_validate_and_clean(args.sync_prefer)
        self._inbox_tasks_controller.inbox_tasks_sync(project_key, sync_prefer)
