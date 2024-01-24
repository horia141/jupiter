"""UseCase for showing the slack tasks."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    actionable_date_to_rich_text,
    difficulty_to_rich_text,
    due_date_to_rich_text,
    eisen_to_rich_text,
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    inbox_task_summary_to_rich_text,
    slack_channel_name_to_rich_text,
    slack_task_message_to_rich_text,
    slack_user_name_to_rich_text,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.use_cases.push_integrations.slack.find import (
    SlackTaskFindResult,
    SlackTaskFindUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class SlackTaskShow(LoggedInReadonlyCommand[SlackTaskFindUseCase]):
    """UseCase class for showing the slack tasks."""

    def _render_result(self, result: SlackTaskFindResult) -> None:
        sorted_slack_tasks = sorted(
            result.entries,
            key=lambda ste: (ste.slack_task.archived, ste.slack_task.created_time),
        )

        rich_tree = Tree("💬 Slack Tasks", guide_style="bold bright_blue")

        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            generation_project_text = Text(
                f"The generation project is {result.generation_project.name}",
            )
            rich_tree.add(generation_project_text)

        for slack_task_entry in sorted_slack_tasks:
            slack_task = slack_task_entry.slack_task
            inbox_task = slack_task_entry.inbox_task
            generation_extra_info = slack_task.generation_extra_info

            slack_task_text = Text("")
            slack_task_text.append(entity_id_to_rich_text(slack_task.ref_id))
            slack_task_text.append(" ")
            slack_task_text.append(slack_user_name_to_rich_text(slack_task.user))
            if slack_task.channel:
                slack_task_text.append(" ")
                slack_task_text.append(
                    slack_channel_name_to_rich_text(slack_task.channel),
                )
            else:
                slack_task_text.append(" as ").append("DM", style="italic green")
            slack_task_text.append(slack_task_message_to_rich_text(slack_task.message))

            slack_task_info_text = Text("")
            should_add_info_text = False

            if generation_extra_info.name:
                should_add_info_text = True
                slack_task_info_text.append("name=")
                slack_task_info_text.append(
                    entity_name_to_rich_text(generation_extra_info.name),
                )
            if generation_extra_info.eisen:
                should_add_info_text = True
                slack_task_info_text.append(" ")
                slack_task_info_text.append(
                    eisen_to_rich_text(generation_extra_info.eisen),
                )
            if generation_extra_info.difficulty:
                should_add_info_text = True
                slack_task_info_text.append(" ")
                slack_task_info_text.append(
                    difficulty_to_rich_text(generation_extra_info.difficulty),
                )
            if generation_extra_info.actionable_date:
                should_add_info_text = True
                slack_task_info_text.append(" ")
                slack_task_info_text.append(
                    actionable_date_to_rich_text(generation_extra_info.actionable_date),
                )
            if generation_extra_info.due_date:
                should_add_info_text = True
                slack_task_info_text.append(" ")
                slack_task_info_text.append(
                    due_date_to_rich_text(generation_extra_info.due_date),
                )

            slack_task_tree = rich_tree.add(
                slack_task_text,
                guide_style="gray62" if slack_task.archived else "blue",
            )
            if should_add_info_text:
                slack_task_tree.add(slack_task_info_text)

            if slack_task.archived:
                slack_task_text.stylize("gray62")
                slack_task_info_text.stylize("gray62")

            if inbox_task is None:
                continue

            inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
            slack_task_tree.add(inbox_task_text)

        console = Console()
        console.print(rich_tree)
