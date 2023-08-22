"""UseCase for updating inbox tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.inbox_tasks.update import (
    InboxTaskUpdateArgs,
    InboxTaskUpdateUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties
from rich.text import Text


class InboxTaskUpdate(LoggedInMutationCommand[InboxTaskUpdateUseCase]):
    """UseCase class for updating inbox tasks."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: InboxTaskUpdateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-task-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the inbox task to modify",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            help="The name of the inbox task",
        )
        parser.add_argument(
            "--status",
            dest="status",
            required=False,
            choices=InboxTaskStatus.all_values(),
            help="The status of the inbox task",
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
            help="The actionable date of the inbox task",
        )
        actionable_date.add_argument(
            "--clear-actionable-date",
            dest="clear_actionable_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the actionable date  of the inbox task",
        )
        due_date = parser.add_mutually_exclusive_group()
        due_date.add_argument(
            "--due-date",
            dest="due_date",
            help="The due date of the inbox task",
        )
        due_date.add_argument(
            "--clear-due-date",
            dest="clear_due_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the due date  of the inbox task",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(InboxTaskName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.status:
            status = UpdateAction.change_to(InboxTaskStatus.from_raw(args.status))
        else:
            status = UpdateAction.do_nothing()
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
                ADate.from_raw(self._global_properties.timezone, args.actionable_date),
            )
        else:
            actionable_date = UpdateAction.do_nothing()
        due_date: UpdateAction[Optional[ADate]]
        if args.clear_due_date:
            due_date = UpdateAction.change_to(None)
        elif args.due_date:
            due_date = UpdateAction.change_to(
                ADate.from_raw(self._global_properties.timezone, args.due_date),
            )
        else:
            due_date = UpdateAction.do_nothing()

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            InboxTaskUpdateArgs(
                ref_id=ref_id,
                name=name,
                status=status,
                eisen=eisen,
                difficulty=difficulty,
                actionable_date=actionable_date,
                due_date=due_date,
            ),
        )

        if result.record_score_result is not None:
            if result.record_score_result.latest_task_score > 0:
                color = "green"
                rich_text = Text("⭐ Congratulations! You scored ")
            else:
                color = "red"
                rich_text = Text("😿 Ah snap! You lost ")

            points = (
                "points"
                if abs(result.record_score_result.latest_task_score) > 1
                else "point"
            )

            rich_text.append(
                f"{abs(result.record_score_result.latest_task_score)} {points}! ",
                style=f"bold {color}",
            )
            rich_text.append(
                f"Which brings your total for today to {result.record_score_result.score_overview.daily_score} and for this week to {result.record_score_result.score_overview.weekly_score}."
            )

            self.mark_postscript(rich_text)
