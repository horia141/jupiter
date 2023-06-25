"""UseCase for hard removing a smart list."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.remove import (
    SmartListRemoveArgs,
    SmartListRemoveUseCase,
)


class SmartListsRemove(LoggedInMutationCommand[SmartListRemoveUseCase]):
    """UseCase for hard removing of a smart list."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list-id",
            dest="smart_list_ref_id",
            required=True,
            help="The key of the smart list to remove",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_ref_id = EntityId.from_raw(args.smart_list_ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListRemoveArgs(ref_id=smart_list_ref_id),
        )
