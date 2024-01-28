"""UseCase for showing the email tasks."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    actionable_date_to_rich_text,
    difficulty_to_rich_text,
    due_date_to_rich_text,
    eisen_to_rich_text,
    email_address_to_rich_text,
    email_task_subject_to_rich_text,
    email_user_name_to_rich_text,
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    inbox_task_summary_to_rich_text,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.use_cases.push_integrations.email.find import (
    EmailTaskFindResult,
    EmailTaskFindUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class EmailTaskShow(LoggedInReadonlyCommand[EmailTaskFindUseCase]):
    """UseCase class for showing the email tasks."""

    def _render_result(self, console: Console, result: EmailTaskFindResult) -> None:
        sorted_email_tasks = sorted(
            result.entries,
            key=lambda ste: (ste.email_task.archived, ste.email_task.created_time),
        )

        rich_tree = Tree("💬 Email Tasks", guide_style="bold bright_blue")

        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            generation_project_text = Text(
                f"The generation project is {result.generation_project.name}",
            )
            rich_tree.add(generation_project_text)

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
                    entity_name_to_rich_text(generation_extra_info.name),
                )
            if generation_extra_info.eisen:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    eisen_to_rich_text(generation_extra_info.eisen),
                )
            if generation_extra_info.difficulty:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    difficulty_to_rich_text(generation_extra_info.difficulty),
                )
            if generation_extra_info.actionable_date:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    actionable_date_to_rich_text(generation_extra_info.actionable_date),
                )
            if generation_extra_info.due_date:
                should_add_info_text = True
                email_task_info_text.append(" ")
                email_task_info_text.append(
                    due_date_to_rich_text(generation_extra_info.due_date),
                )

            email_task_tree = rich_tree.add(
                email_task_text,
                guide_style="gray62" if email_task.archived else "blue",
            )
            if should_add_info_text:
                email_task_tree.add(email_task_info_text)

            if email_task.archived:
                email_task_text.stylize("gray62")
                email_task_info_text.stylize("gray62")

            if inbox_task is None:
                continue

            inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
            email_task_tree.add(inbox_task_text)

        console.print(rich_tree)
