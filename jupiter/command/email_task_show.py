"""UseCase for showing the email tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_id_to_rich_text,
    inbox_task_summary_to_rich_text,
    email_user_name_to_rich_text,
    entity_name_to_rich_text,
    eisen_to_rich_text,
    difficulty_to_rich_text,
    actionable_date_to_rich_text,
    due_date_to_rich_text,
    RichConsoleProgressReporter,
    email_task_subject_to_rich_text,
    email_address_to_rich_text,
)
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.push_integrations.email.find import EmailTaskFindUseCase
from jupiter.utils.global_properties import GlobalProperties


class EmailTaskShow(command.ReadonlyCommand):
    """UseCase class for showing the email tasks."""

    _global_properties: Final[GlobalProperties]
    _command: Final[EmailTaskFindUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: EmailTaskFindUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "email-task-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of email tasks"

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
        show_inbox_tasks = args.show_inbox_tasks

        result = self._command.execute(
            progress_reporter,
            EmailTaskFindUseCase.Args(
                allow_archived=show_archived, filter_ref_ids=ref_ids
            ),
        )

        sorted_email_tasks = sorted(
            result.email_tasks,
            key=lambda ste: (ste.email_task.archived, ste.email_task.created_time),
        )

        rich_tree = Tree("💬 Email Tasks", guide_style="bold bright_blue")

        for email_task_entry in sorted_email_tasks:
            email_task = email_task_entry.email_task
            inbox_task = email_task_entry.inbox_task
            generation_extra_info = email_task.generation_extra_info

            email_task_text = Text("")
            email_task_text.append(entity_id_to_rich_text(email_task.ref_id))
            email_task_text.append(" ")
            email_task_text.append(email_user_name_to_rich_text(email_task.from_name))
            email_task_text.append(" <")
            email_task_text.append(email_address_to_rich_text(email_task.from_address))
            email_task_text.append("> to ")
            email_task_text.append(email_address_to_rich_text(email_task.to_address))
            email_task_text.append(" ")
            email_task_text.append(email_task_subject_to_rich_text(email_task.subject))

            email_task_info_text = Text("")
            should_add_info_text = False

            if generation_extra_info.name:
                should_add_info_text = True
                email_task_info_text.append("name=")
                email_task_info_text.append(
                    entity_name_to_rich_text(generation_extra_info.name)
                )
            if generation_extra_info.eisen:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    eisen_to_rich_text(generation_extra_info.eisen)
                )
            if generation_extra_info.difficulty:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    difficulty_to_rich_text(generation_extra_info.difficulty)
                )
            if generation_extra_info.actionable_date:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    actionable_date_to_rich_text(generation_extra_info.actionable_date)
                )
            if generation_extra_info.due_date:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    due_date_to_rich_text(generation_extra_info.due_date)
                )

            email_task_tree = rich_tree.add(
                email_task_text, guide_style="gray62" if email_task.archived else "blue"
            )
            if should_add_info_text:
                email_task_tree.add(email_task_info_text)

            if email_task.archived:
                email_task_text.stylize("gray62")
                email_task_info_text.stylize("gray62")

            if not show_inbox_tasks:
                continue
            if inbox_task is None:
                continue

            inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
            email_task_tree.add(inbox_task_text)

        console = Console()
        console.print(rich_tree)
