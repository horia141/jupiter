"""UseCase for associating an inbox task with a big plan."""

from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.inbox_tasks.associate_with_big_plan import (
    InboxTaskAssociateWithBigPlanArgs,
    InboxTaskAssociateWithBigPlanUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class InboxTaskAssociateWithBigPlan(
    LoggedInMutationCommand[InboxTaskAssociateWithBigPlanUseCase]
):
    """UseCase class for associating an inbox task with a big plan."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The if of the big plan",
        )
        big_plan = parser.add_mutually_exclusive_group()
        big_plan.add_argument(
            "--big-plan-id",
            type=str,
            dest="big_plan_ref_id",
            help="The id of a big plan to associate this task to.",
        )
        big_plan.add_argument(
            "--clear-big-plan",
            dest="clear_big_plan",
            default=False,
            action="store_const",
            const=True,
            help="Clear the big plan",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.clear_big_plan:
            big_plan_ref_id = None
        else:
            big_plan_ref_id = EntityId.from_raw(args.big_plan_ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            InboxTaskAssociateWithBigPlanArgs(
                ref_id=ref_id,
                big_plan_ref_id=big_plan_ref_id,
            ),
        )
