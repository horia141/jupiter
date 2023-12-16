"""UseCase for creating an inbox task."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.inbox_tasks.create import (
    InboxTaskCreateArgs,
    InboxTaskCreateUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties


class InboxTaskCreate(LoggedInMutationCommand[InboxTaskCreateUseCase]):
    """UseCase class for creating inbox tasks."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: InboxTaskCreateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-task-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            parser.add_argument(
                "--project-id",
                dest="project_ref_id",
                required=False,
                help="The key of the project",
            )
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the inbox task",
        )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.BIG_PLANS
        ):
            parser.add_argument(
                "--big-plan-id",
                type=str,
                dest="big_plan_ref_id",
                help="The id of a big plan to associate this task to.",
            )
        parser.add_argument(
            "--eisen",
            dest="eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for task",
        )
        parser.add_argument(
            "--difficulty",
            dest="difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for tasks",
        )
        parser.add_argument(
            "--actionable-date",
            dest="actionable_date",
            help="The active date of the inbox task",
        )
        parser.add_argument(
            "--due-date",
            dest="due_date",
            help="The due date of the big plan",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            project_ref_id = (
                EntityId.from_raw(args.project_ref_id) if args.project_ref_id else None
            )
        else:
            project_ref_id = None
        name = InboxTaskName.from_raw(args.name)
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.BIG_PLANS
        ):
            big_plan_ref_id = (
                EntityId.from_raw(args.big_plan_ref_id)
                if args.big_plan_ref_id
                else None
            )
        else:
            big_plan_ref_id = None
        eisen = Eisen.from_raw(args.eisen) if args.eisen else None
        difficulty = Difficulty.from_raw(args.difficulty) if args.difficulty else None
        actionable_date = (
            ADate.from_raw(self._global_properties.timezone, args.actionable_date)
            if args.actionable_date
            else None
        )
        due_date = (
            ADate.from_raw(self._global_properties.timezone, args.due_date)
            if args.due_date
            else None
        )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            InboxTaskCreateArgs(
                project_ref_id=project_ref_id,
                name=name,
                big_plan_ref_id=big_plan_ref_id,
                eisen=eisen,
                difficulty=difficulty,
                actionable_date=actionable_date,
                due_date=due_date,
            ),
        )
