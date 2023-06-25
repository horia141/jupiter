"""UseCase for archiving a smart list."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.archive import (
    SmartListArchiveArgs,
    SmartListArchiveUseCase,
)


class SmartListArchive(LoggedInMutationCommand[SmartListArchiveUseCase]):
    """UseCase for archiving of a smart list."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The key of the smart list to archive",
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
            SmartListArchiveArgs(ref_id=ref_id),
        )
