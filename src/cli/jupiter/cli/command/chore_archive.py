"""UseCase for removing a chore."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.chores.archive import ChoreArchiveArgs, ChoreArchiveUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class ChoreArchive(LoggedInMutationCommand[ChoreArchiveUseCase]):
    """UseCase class for removing a chore."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a chore"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the vacations to modify",
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
            ChoreArchiveArgs(ref_id),
        )
