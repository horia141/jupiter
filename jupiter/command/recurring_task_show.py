"""UseCase for showing the recurring tasks."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.adate import ADate
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.recurring_tasks.find import RecurringTaskFindUseCase
from jupiter.utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class RecurringTaskShow(command.Command):
    """UseCase class for showing the recurring tasks."""

    _global_properties: Final[GlobalProperties]
    _command: Final[RecurringTaskFindUseCase]

    def __init__(
            self, global_properties: GlobalProperties, the_command: RecurringTaskFindUseCase) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-task-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of recurring tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the vacations to show")
        parser.add_argument("--project", type=str, dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        project_keys = [ProjectKey.from_raw(p) for p in args.project_keys] \
            if len(args.project_keys) > 0 else None
        response = self._command.execute(RecurringTaskFindUseCase.Args(
            show_archived=False, filter_ref_ids=ref_ids, filter_project_keys=project_keys))

        for recurring_task_entry in response.recurring_tasks:
            recurring_task = recurring_task_entry.recurring_task
            inbox_tasks = recurring_task_entry.inbox_tasks
            difficulty_str = \
                recurring_task.gen_params.difficulty.value if recurring_task.gen_params.difficulty else "none"
            print(f'id={recurring_task.ref_id} {recurring_task.name}' +
                  f' type={recurring_task.the_type.value}' +
                  f'\n    eisen="{recurring_task.gen_params.eisen.value}"' +
                  f' difficulty={difficulty_str}' +
                  f' skip_rule={recurring_task.skip_rule or "none"}' +
                  f' suspended={recurring_task.suspended}' +
                  f' must_do={recurring_task.must_do}' +
                  (f' start_at_date={recurring_task.start_at_date}' if recurring_task.start_at_date else '') +
                  (f' end_at_date={recurring_task.end_at_date}' if recurring_task.end_at_date else '') +
                  f'\n    due_at_time={recurring_task.gen_params.due_at_time or "none"}' +
                  f' due_at_day={recurring_task.gen_params.due_at_day or "none"}' +
                  f' due_at_month={recurring_task.gen_params.due_at_month or "none"}')
            print("  Tasks:")

            for inbox_task in inbox_tasks:
                print(f'   - id={inbox_task.ref_id} {inbox_task.name}' +
                      f' status={inbox_task.status.value}' +
                      f' archived="{inbox_task.archived}"' +
                      f' due_date="{ADate.to_user_str(self._global_properties.timezone, inbox_task.due_date)}"')
