"""UseCase for updating slack tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.command import command
from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.push_integrations.slack.slack_channel_name import SlackChannelName
from jupiter.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.update_action import UpdateAction
from jupiter.use_cases.push_integrations.slack.update import SlackTaskUpdateUseCase
from jupiter.utils.global_properties import GlobalProperties


class SlackTaskUpdate(command.Command):
    """UseCase class for updating slack tasks."""

    _global_properties: Final[GlobalProperties]
    _command: Final[SlackTaskUpdateUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: SlackTaskUpdateUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "slack-task-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a slack task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the slack task to modify",
        )
        parser.add_argument(
            "--user",
            dest="user",
            required=False,
            help="The name of the Slack user from the message",
        )
        channel = parser.add_mutually_exclusive_group()
        channel.add_argument(
            "--channel",
            dest="channel",
            help="The channel on which the Slack message was posted",
        )
        channel.add_argument(
            "--clear-channel",
            dest="clear_channel",
            default=False,
            action="store_const",
            const=True,
            help="Clear the channel for the Slack message and assume it was a DM",
        )
        parser.add_argument(
            "--message", dest="message", required=False, help="The Slack message"
        )
        name = parser.add_mutually_exclusive_group()
        name.add_argument("--name", dest="name", help="The name of the generated task")
        channel.add_argument(
            "--clear-name",
            dest="clear_name",
            default=False,
            action="store_const",
            const=True,
            help="Clear the name of the generated task and use an auto-generated one",
        )
        parser.add_argument(
            "--status",
            dest="status",
            required=False,
            choices=InboxTaskStatus.all_values(),
            help="The status of the generated inbox task",
        )
        parser.add_argument(
            "--eisen",
            dest="eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for the task",
        )
        difficulty = parser.add_mutually_exclusive_group()
        difficulty.add_argument(
            "--difficulty",
            dest="difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for tasks",
        )
        difficulty.add_argument(
            "--clear-difficulty",
            dest="clear_difficulty",
            default=False,
            action="store_const",
            const=True,
            help="Clear the difficulty  of the inbox task",
        )
        actionable_date = parser.add_mutually_exclusive_group()
        actionable_date.add_argument(
            "--actionable-date",
            dest="actionable_date",
            help="The actionable date of the slack task",
        )
        actionable_date.add_argument(
            "--clear-actionable-date",
            dest="clear_actionable_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the actionable date of the slack task",
        )
        due_date = parser.add_mutually_exclusive_group()
        due_date.add_argument(
            "--due-date", dest="due_date", help="The due date of the slack task"
        )
        due_date.add_argument(
            "--clear-due-date",
            dest="clear_due_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the due date of the slack task",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.entity_id)
        if args.user:
            user = UpdateAction.change_to(SlackUserName.from_raw(args.name))
        else:
            user = UpdateAction.do_nothing()
        channel: UpdateAction[Optional[SlackChannelName]]
        if args.clear_channel:
            channel = UpdateAction.change_to(None)
        elif args.channel:
            channel = UpdateAction.change_to(SlackChannelName.from_raw(args.channel))
        else:
            channel = UpdateAction.do_nothing()
        if args.message:
            message = UpdateAction.change_to(args.name)
        else:
            message = UpdateAction.do_nothing()
        name: UpdateAction[Optional[InboxTaskName]]
        if args.clear_name:
            name = UpdateAction.change_to(None)
        elif args.name:
            name = UpdateAction.change_to(InboxTaskName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        status: UpdateAction[Optional[InboxTaskStatus]]
        if args.status:
            status = UpdateAction.change_to(InboxTaskStatus.from_raw(args.status))
        else:
            status = UpdateAction.do_nothing()
        eisen: UpdateAction[Optional[Eisen]]
        if args.eisen:
            eisen = UpdateAction.change_to(Eisen.from_raw(args.eisen))
        else:
            eisen = UpdateAction.do_nothing()
        difficulty: UpdateAction[Optional[Difficulty]]
        if args.clear_difficulty:
            difficulty = UpdateAction.change_to(None)
        elif args.difficulty:
            difficulty = UpdateAction.change_to(Difficulty.from_raw(args.difficulty))
        else:
            difficulty = UpdateAction.do_nothing()
        actionable_date: UpdateAction[Optional[ADate]]
        if args.clear_actionable_date:
            actionable_date = UpdateAction.change_to(None)
        elif args.actionable_date:
            actionable_date = UpdateAction.change_to(
                ADate.from_raw(self._global_properties.timezone, args.actionable_date)
            )
        else:
            actionable_date = UpdateAction.do_nothing()
        due_date: UpdateAction[Optional[ADate]]
        if args.clear_due_date:
            due_date = UpdateAction.change_to(None)
        elif args.due_date:
            due_date = UpdateAction.change_to(
                ADate.from_raw(self._global_properties.timezone, args.due_date)
            )
        else:
            due_date = UpdateAction.do_nothing()
        self._command.execute(
            SlackTaskUpdateUseCase.Args(
                ref_id=ref_id,
                user=user,
                channel=channel,
                message=message,
                generation_name=name,
                generation_status=status,
                generation_eisen=eisen,
                generation_difficulty=difficulty,
                generation_actionable_date=actionable_date,
                generation_due_datee=due_date,
            )
        )
