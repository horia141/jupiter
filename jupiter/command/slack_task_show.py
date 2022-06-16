"""UseCase for showing the slack tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.adate import ADate
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.push_integrations.slack.find import SlackTaskFindUseCase
from jupiter.utils.global_properties import GlobalProperties


class SlackTaskShow(command.Command):
    """UseCase class for showing the slack tasks."""

    _global_properties: Final[GlobalProperties]
    _command: Final[SlackTaskFindUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: SlackTaskFindUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

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

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = (
            [EntityId.from_raw(rid) for rid in args.ref_ids]
            if len(args.ref_ids) > 0
            else None
        )

        result = self._command.execute(
            SlackTaskFindUseCase.Args(
                allow_archived=show_archived, filter_ref_ids=ref_ids
            )
        )

        for slack_task_entry in result.slack_tasks:
            slack_task = slack_task_entry.slack_task
            inbox_task = slack_task_entry.inbox_task
            timezone = slack_task.generation_extra_info.timezone
            generation_extra_info = slack_task.generation_extra_info
            print(
                f"id={slack_task.ref_id} from={slack_task.user} "
                + f'in-channel={str(slack_task.channel) if slack_task.channel else "DM"}'
                + f" message={slack_task.message[0:100]}"
                + f" archived={slack_task.archived}"
                + f' {"Has task" if slack_task.has_generated_task else "No task yet"}'
                + f" name={slack_task.generation_extra_info.name}"
                + f" eisen={generation_extra_info.eisen.for_notion() if generation_extra_info.eisen else 'None'}"
                + f" difficulty={generation_extra_info.difficulty.for_notion() if generation_extra_info.difficulty else 'None'}"
                + f" status={generation_extra_info.status.for_notion() if generation_extra_info.status else 'None'}"
                + f" actionable-date={ADate.to_user_str(timezone, slack_task.generation_extra_info.actionable_date)}"
                + f" due-date={ADate.to_user_str(timezone, slack_task.generation_extra_info.due_date)}"
            )
            if inbox_task:
                print("  Task:")
                print(
                    f"   - id={inbox_task.ref_id} {inbox_task.name}"
                    + f" status={inbox_task.status.value}"
                    + f" archived={inbox_task.archived}"
                    + f' due_date="{ADate.to_user_str(self._global_properties.timezone, inbox_task.due_date)}"'
                )
