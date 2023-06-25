"""UseCase for showing the slack tasks."""
from argparse import ArgumentParser, Namespace

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
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.push_integrations.slack.find import (
    SlackTaskFindArgs,
    SlackTaskFindUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class SlackTaskShow(LoggedInReadonlyCommand[SlackTaskFindUseCase]):
    """UseCase class for showing the slack tasks."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "slack-task-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of slack tasks"

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

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = (
            [EntityId.from_raw(rid) for rid in args.ref_ids]
            if len(args.ref_ids) > 0
            else None
        )
        show_inbox_tasks = args.show_inbox_tasks

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SlackTaskFindArgs(
                allow_archived=show_archived,
                include_inbox_tasks=show_inbox_tasks,
                filter_ref_ids=ref_ids,
            ),
        )

        sorted_slack_tasks = sorted(
            result.entries,
            key=lambda ste: (ste.slack_task.archived, ste.slack_task.created_time),
        )

        rich_tree = Tree("💬 Slack Tasks", guide_style="bold bright_blue")

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

            if not show_inbox_tasks:
                continue
            if inbox_task is None:
                continue

            inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
            slack_task_tree.add(inbox_task_text)

        console = Console()
        console.print(rich_tree)
