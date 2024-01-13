"""UseCase for updating email tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.push_integrations.email.update import (
    EmailTaskUpdateArgs,
    EmailTaskUpdateUseCase,
)
from jupiter.core.utils.global_properties import GlobalProperties


class EmailTaskUpdate(LoggedInMutationCommand[EmailTaskUpdateUseCase]):
    """UseCase class for updating email tasks."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: EmailTaskUpdateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "email-task-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update an email task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the email task to modify",
        )
        parser.add_argument(
            "--from-address",
            dest="from_address",
            required=False,
            help="The email address the message comes from",
        )
        parser.add_argument(
            "--from-name",
            dest="from_name",
            required=False,
            help="The name of the person the message comes from",
        )
        parser.add_argument(
            "--to-address",
            dest="to_address",
            required=False,
            help="Which of your email addresses the message was sent to",
        )
        parser.add_argument(
            "--subject",
            dest="subject",
            required=False,
            help="The subject of the message",
        )
        parser.add_argument(
            "--body",
            dest="subject",
            required=False,
            help="The body of the message",
        )
        name = parser.add_mutually_exclusive_group()
        name.add_argument("--name", dest="name", help="The name of the generated task")
        name.add_argument(
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
            help="The actionable date of the email task",
        )
        actionable_date.add_argument(
            "--clear-actionable-date",
            dest="clear_actionable_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the actionable date of the email task",
        )
        due_date = parser.add_mutually_exclusive_group()
        due_date.add_argument(
            "--due-date",
            dest="due_date",
            help="The due date of the email task",
        )
        due_date.add_argument(
            "--clear-due-date",
            dest="clear_due_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the due date of the email task",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.from_address:
            from_address = UpdateAction.change_to(
                EmailAddress.from_raw(args.from_address),
            )
        else:
            from_address = UpdateAction.do_nothing()
        if args.from_name:
            from_name = UpdateAction.change_to(EmailUserName.from_raw(args.from_name))
        else:
            from_name = UpdateAction.do_nothing()
        if args.to_address:
            to_address = UpdateAction.change_to(EmailAddress.from_raw(args.to_address))
        else:
            to_address = UpdateAction.do_nothing()
        if args.subject:
            subject = UpdateAction.change_to(args.subject)
        else:
            subject = UpdateAction.do_nothing()
        if args.body:
            body = UpdateAction.change_to(args.body)
        else:
            body = UpdateAction.do_nothing()
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
                ADate.from_raw_in_tz(
                    self._global_properties.timezone, args.actionable_date
                ),
            )
        else:
            actionable_date = UpdateAction.do_nothing()
        due_date: UpdateAction[Optional[ADate]]
        if args.clear_due_date:
            due_date = UpdateAction.change_to(None)
        elif args.due_date:
            due_date = UpdateAction.change_to(
                ADate.from_raw_in_tz(self._global_properties.timezone, args.due_date),
            )
        else:
            due_date = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            EmailTaskUpdateArgs(
                ref_id=ref_id,
                from_address=from_address,
                from_name=from_name,
                to_address=to_address,
                subject=subject,
                body=body,
                generation_name=name,
                generation_status=status,
                generation_eisen=eisen,
                generation_difficulty=difficulty,
                generation_actionable_date=actionable_date,
                generation_due_date=due_date,
            ),
        )
