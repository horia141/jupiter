"""UseCase for showing the big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_id_to_rich_text,
    actionable_date_to_rich_text,
    due_date_to_rich_text,
    project_to_rich_text,
    big_plan_status_to_rich_text,
    inbox_task_summary_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.domain.adate import ADate
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.big_plans.find import BigPlanFindUseCase


class BigPlanShow(command.ReadonlyCommand):
    """UseCase class for showing the big plans."""

    _command: Final[BigPlanFindUseCase]

    def __init__(self, the_command: BigPlanFindUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plan-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of big plans"

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
            help="The id of the vacations to modify",
        )
        parser.add_argument(
            "--project",
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
            [ProjectKey.from_raw(pk) for pk in args.project_keys]
            if len(args.project_keys) > 0
            else None
        )
        show_inbox_tasks = args.show_inbox_tasks

        result = self._command.execute(
            progress_reporter,
            BigPlanFindUseCase.Args(
                allow_archived=show_archived,
                filter_ref_ids=ref_ids,
                filter_project_keys=project_keys,
            ),
        )

        sorted_big_plans = sorted(
            result.big_plans,
            key=lambda bpe: (
                bpe.big_plan.archived,
                bpe.big_plan.status,
                bpe.big_plan.actionable_date
                if bpe.big_plan.actionable_date
                else ADate.from_str("2100-01-01"),
            ),
        )

        rich_tree = Tree("🌍 Big Plans", guide_style="bold bright_blue")

        for big_plan_entry in sorted_big_plans:
            big_plan = big_plan_entry.big_plan
            project = big_plan_entry.project
            inbox_tasks = big_plan_entry.inbox_tasks

            big_plan_text = big_plan_status_to_rich_text(
                big_plan.status, big_plan.archived
            )
            big_plan_text.append(" ")
            big_plan_text.append(entity_id_to_rich_text(big_plan.ref_id))
            big_plan_text.append(f" {big_plan.name}")

            big_plan_info_text = Text("")
            if big_plan.actionable_date is not None:
                big_plan_info_text.append(
                    actionable_date_to_rich_text(big_plan.actionable_date)
                )

            if big_plan.due_date is not None:
                big_plan_info_text.append(" ")
                big_plan_info_text.append(due_date_to_rich_text(big_plan.due_date))

            big_plan_info_text.append(" ")
            big_plan_info_text.append(project_to_rich_text(project.name))

            if big_plan.archived:
                big_plan_text.stylize("gray62")
                big_plan_info_text.stylize("gray62")

            big_plan_tree = rich_tree.add(
                big_plan_text, guide_style="gray62" if big_plan.archived else "blue"
            )
            big_plan_tree.add(big_plan_info_text)

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
                big_plan_tree.add(inbox_task_text)

        console = Console()
        console.print(rich_tree)
