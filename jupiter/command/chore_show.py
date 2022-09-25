"""UseCase for showing the chores."""
from argparse import ArgumentParser, Namespace
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_id_to_rich_text,
    period_to_rich_text,
    eisen_to_rich_text,
    difficulty_to_rich_text,
    skip_rule_to_rich_text,
    start_date_to_rich_text,
    end_date_to_rich_text,
    project_to_rich_text,
    due_at_time_to_rich_text,
    due_at_day_to_rich_text,
    due_at_month_to_rich_text,
    inbox_task_summary_to_rich_text,
    actionable_from_day_to_rich_text,
    actionable_from_month_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.chores.find import ChoreFindUseCase
from jupiter.utils.global_properties import GlobalProperties


class ChoreShow(command.ReadonlyCommand):
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
        parser.add_argument(
            "--show-inbox-tasks",
            dest="show_inbox_tasks",
            default=False,
            action="store_const",
            const=True,
            help="Show inbox tasks",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
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
        show_inbox_tasks = args.show_inbox_tasks

        result = self._command.execute(
            progress_reporter,
            ChoreFindUseCase.Args(
                show_archived=show_archived,
                filter_ref_ids=ref_ids,
                filter_project_keys=project_keys,
            ),
        )

        rich_tree = Tree("♻️  Chores", guide_style="bold bright_blue")

        sorted_chores = sorted(
            result.chores,
            key=lambda ce: (
                ce.chore.archived,
                ce.chore.suspended,
                ce.chore.gen_params.period,
                ce.chore.gen_params.eisen,
                ce.chore.gen_params.difficulty or Difficulty.EASY,
            ),
        )

        for chore_entry in sorted_chores:
            chore = chore_entry.chore
            project = chore_entry.project
            inbox_tasks = chore_entry.inbox_tasks

            chore_text = Text("")
            chore_text.append(entity_id_to_rich_text(chore.ref_id))
            chore_text.append(f" {chore.name}")

            chore_info_text = Text("")
            chore_info_text.append(period_to_rich_text(chore.gen_params.period))
            chore_info_text.append(" ")
            chore_info_text.append(eisen_to_rich_text(chore.gen_params.eisen))

            if chore.gen_params.difficulty:
                chore_info_text.append(" ")
                chore_info_text.append(
                    difficulty_to_rich_text(chore.gen_params.difficulty)
                )

            if chore.skip_rule and str(chore.skip_rule) != "none":
                chore_info_text.append(" ")
                chore_info_text.append(skip_rule_to_rich_text(chore.skip_rule))

            if chore.gen_params.actionable_from_day:
                chore_info_text.append(" ")
                chore_info_text.append(
                    actionable_from_day_to_rich_text(
                        chore.gen_params.actionable_from_day
                    )
                )

            if chore.gen_params.actionable_from_month:
                chore_info_text.append(" ")
                chore_info_text.append(
                    actionable_from_month_to_rich_text(
                        chore.gen_params.actionable_from_month
                    )
                )

            if chore.gen_params.due_at_time:
                chore_info_text.append(" ")
                chore_info_text.append(
                    due_at_time_to_rich_text(chore.gen_params.due_at_time)
                )

            if chore.gen_params.due_at_day:
                chore_info_text.append(" ")
                chore_info_text.append(
                    due_at_day_to_rich_text(chore.gen_params.due_at_day)
                )

            if chore.gen_params.due_at_month:
                chore_info_text.append(" ")
                chore_info_text.append(
                    due_at_month_to_rich_text(chore.gen_params.due_at_month)
                )

            if chore.start_at_date:
                chore_info_text.append(" ")
                chore_info_text.append(start_date_to_rich_text(chore.start_at_date))

            if chore.end_at_date:
                chore_info_text.append(" ")
                chore_info_text.append(end_date_to_rich_text(chore.end_at_date))

            chore_info_text.append(" ")
            chore_info_text.append(project_to_rich_text(project.name))

            if chore.suspended:
                chore_text.stylize("yellow")
                chore_info_text.append(" #suspended")
                chore_info_text.stylize("yellow")

            if chore.archived:
                chore_text.stylize("gray62")
                chore_info_text.stylize("gray62")

            chore_tree = rich_tree.add(
                chore_text, guide_style="gray62" if chore.archived else "blue"
            )
            chore_tree.add(chore_info_text)

            if not show_inbox_tasks:
                continue
            if len(inbox_tasks) == 0:
                continue

            sorted_inbox_tasks = sorted(
                inbox_tasks,
                key=lambda it: (
                    it.archived,
                    it.status,
                    it.due_date if it.due_date else ADate.from_str("2100-01-01"),
                ),
            )

            for inbox_task in sorted_inbox_tasks:
                inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
                chore_tree.add(inbox_task_text)

        console = Console()
        console.print(rich_tree)
