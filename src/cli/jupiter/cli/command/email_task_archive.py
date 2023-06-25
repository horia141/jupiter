"""UseCase for archiving a email task."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.push_integrations.email.archive import (
    EmailTaskArchiveArgs,
    EmailTaskArchiveUseCase,
)


class EmailTaskArchive(LoggedInMutationCommand[EmailTaskArchiveUseCase]):
    """UseCase class for archiving an email task."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "email-task-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive an email task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The if of the email task",
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
            EmailTaskArchiveArgs(ref_id),
        )
