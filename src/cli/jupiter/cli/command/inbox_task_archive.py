"""UseCase for archiving an inbox task."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.inbox_tasks.archive import (
    InboxTaskArchiveArgs,
    InboxTaskArchiveUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class InboxTaskArchive(LoggedInMutationCommand[InboxTaskArchiveUseCase]):
    """UseCase class for archiving an inbox task."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-task-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The if of the big plan",
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
            InboxTaskArchiveArgs(ref_id),
        )
