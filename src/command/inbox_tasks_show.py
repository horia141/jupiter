"""Command for showing the inbox tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.framework import EntityId
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class InboxTasksShow(command.Command):
    """Command class for showing the inbox tasks."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(
            self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of inbox tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="Show only tasks selected by this id")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")
        parser.add_argument("--source", dest="sources", default=[], action="append",
                            choices=BasicValidator.inbox_task_source_values(),
                            help="Allow only inbox tasks form this particular source. Defaults to all")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]\
            if len(args.ref_ids) > 0 else None
        project_keys = [self._basic_validator.project_key_validate_and_clean(p) for p in args.project_keys]\
            if len(args.project_keys) > 0 else None
        sources = [self._basic_validator.inbox_task_source_validate_and_clean(s) for s in args.sources]\
            if len(args.sources) > 0 else None
        response = self._inbox_tasks_controller.load_all_inbox_tasks(
            filter_ref_ids=ref_ids, filter_project_keys=project_keys, filter_sources=sources)

        for inbox_task_entry in response.inbox_tasks:
            inbox_task = inbox_task_entry.inbox_task
            big_plan = inbox_task_entry.big_plan
            recurring_task = inbox_task_entry.recurring_task
            print(f'id={inbox_task.ref_id} {inbox_task.name}' +
                  f' source={inbox_task.source.for_notion()}' +
                  f' status={inbox_task.status.value}' +
                  f' archived="{inbox_task.archived}"' +
                  (f' big_plan="{big_plan.name}"' if big_plan else "") +
                  (f' recurring_task="{recurring_task.name}"' if recurring_task else "") +
                  f' due_date="{self._basic_validator.adate_to_user(inbox_task.due_date)}"' +
                  f'\n    created_time="{inbox_task.created_time.to_datetime_string()}"' +
                  f' eisen={",".join(e.for_notion() for e in inbox_task.eisen)}' +
                  f' difficulty={inbox_task.difficulty.for_notion() if inbox_task.difficulty else ""}')
