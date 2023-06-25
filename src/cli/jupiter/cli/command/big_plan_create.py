"""UseCase for creating big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.big_plans.create import (
    BigPlanCreateArgs,
    BigPlanCreateUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties


class BigPlanCreate(LoggedInMutationCommand[BigPlanCreateUseCase]):
    """UseCase class for creating big plans."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        use_case: BigPlanCreateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plan-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a big plan"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--project-id",
            dest="project_ref_id",
            required=False,
            help="The id of the project",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the big plan",
        )
        parser.add_argument(
            "--actionable-date",
            dest="actionable_date",
            help="The actionable date of the big plan",
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
        project_ref_id = (
            EntityId.from_raw(args.project_ref_id) if args.project_ref_id else None
        )
        name = BigPlanName.from_raw(args.name)
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
            BigPlanCreateArgs(
                project_ref_id=project_ref_id,
                name=name,
                actionable_date=actionable_date,
                due_date=due_date,
            ),
        )
