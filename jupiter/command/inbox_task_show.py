"""UseCase for showing the inbox tasks."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.adate import ADate
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.inbox_tasks.find import InboxTaskFindUseCase
from jupiter.utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class InboxTaskShow(command.Command):
    """UseCase class for showing the inbox tasks."""

    _global_properties: Final[GlobalProperties]
    _command: Final[InboxTaskFindUseCase]

    def __init__(
            self, global_properties: GlobalProperties, the_command: InboxTaskFindUseCase) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-task-show"

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
                            choices=InboxTaskSource.all_values(),
                            help="Allow only inbox tasks form this particular source. Defaults to all")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]\
            if len(args.ref_ids) > 0 else None
        project_keys = [ProjectKey.from_raw(p) for p in args.project_keys] if len(args.project_keys) > 0 else None
        sources = [InboxTaskSource.from_raw(s) for s in args.sources]\
            if len(args.sources) > 0 else None
        response = self._command.execute(InboxTaskFindUseCase.Args(
            filter_ref_ids=ref_ids, filter_project_keys=project_keys, filter_sources=sources))

        for inbox_task_entry in response.inbox_tasks:
            inbox_task = inbox_task_entry.inbox_task
            habit = inbox_task_entry.habit
            chore = inbox_task_entry.chore
            big_plan = inbox_task_entry.big_plan
            print(f'id={inbox_task.ref_id} {inbox_task.name}' +
                  f' source={inbox_task.source.for_notion()}' +
                  f' status={inbox_task.status.value}' +
                  f' archived="{inbox_task.archived}"' +
                  (f' habit="{habit.name}"' if habit else "") +
                  (f' habit="{chore.name}"' if chore else "") +
                  (f' big_plan="{big_plan.name}"' if big_plan else "") +
                  f' due_date="{ADate.to_user_str(self._global_properties.timezone, inbox_task.due_date)}"' +
                  f'\n    created_time="{inbox_task.created_time}"' +
                  f' eisen={inbox_task.eisen.for_notion()}' +
                  f' difficulty={inbox_task.difficulty.for_notion() if inbox_task.difficulty else ""}')
