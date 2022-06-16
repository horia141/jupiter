"""UseCase for showing the chores."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.adate import ADate
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.chores.find import ChoreFindUseCase
from jupiter.utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class ChoreShow(command.Command):
    """UseCase class for showing the chores."""

    _global_properties: Final[GlobalProperties]
    _command: Final[ChoreFindUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: ChoreFindUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of chores"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--show-archived",
            dest="show_archived",
            default=False,
            action="store_true",
            help="Whether to show archived vacations or not",
        )
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_ids",
            default=[],
            action="append",
            help="The id of the vacations to show",
        )
        parser.add_argument(
            "--project",
            type=str,
            dest="project_keys",
            default=[],
            action="append",
            help="Allow only tasks from this project",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = (
            [EntityId.from_raw(rid) for rid in args.ref_ids]
            if len(args.ref_ids) > 0
            else None
        )
        project_keys = (
            [ProjectKey.from_raw(p) for p in args.project_keys]
            if len(args.project_keys) > 0
            else None
        )
        response = self._command.execute(
            ChoreFindUseCase.Args(
                show_archived=show_archived,
                filter_ref_ids=ref_ids,
                filter_project_keys=project_keys,
            )
        )

        for chore_entry in response.chores:
            chore = chore_entry.chore
            project = chore_entry.project
            inbox_tasks = chore_entry.inbox_tasks
            difficulty_str = (
                chore.gen_params.difficulty.for_notion()
                if chore.gen_params.difficulty
                else "none"
            )
            print(
                f"id={chore.ref_id} {chore.name} period={chore.gen_params.period.for_notion()}"
                + f"\n    eisen={chore.gen_params.eisen.for_notion()}"
                + f" difficulty={difficulty_str}"
                + f' skip_rule={chore.skip_rule or "none"}'
                + f" suspended={chore.suspended}"
                + f" archived={chore.archived}"
                + (
                    f" start_at_date={chore.start_at_date}"
                    if chore.start_at_date
                    else ""
                )
                + (f" end_at_date={chore.end_at_date}" if chore.end_at_date else "")
                + f'\n    due_at_time={chore.gen_params.due_at_time or "none"}'
                + f' due_at_day={chore.gen_params.due_at_day or "none"}'
                + f' due_at_month={chore.gen_params.due_at_month or "none"}'
                + f" project={project.name}"
            )
            print("  Tasks:")

            for inbox_task in inbox_tasks:
                print(
                    f"   - id={inbox_task.ref_id} {inbox_task.name}"
                    + f" status={inbox_task.status.value}"
                    + f" archived={inbox_task.archived}"
                    + f' due_date="{ADate.to_user_str(self._global_properties.timezone, inbox_task.due_date)}"'
                )
