"""UseCase for hard removing a smart list tag."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.tag.remove import (
    SmartListTagRemoveArgs,
    SmartListTagRemoveUseCase,
)


class SmartListTagRemove(LoggedInMutationCommand[SmartListTagRemoveUseCase]):
    """UseCase for hard removing a smart list tag."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-tag-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the smart list tag to hard remove",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListTagRemoveArgs(ref_id=ref_id),
        )
