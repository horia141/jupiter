"""UseCase for archiving projects."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.projects.archive import (
    ProjectArchiveArgs,
    ProjectArchiveUseCase,
)


class ProjectArchive(LoggedInMutationCommand[ProjectArchiveUseCase]):
    """UseCase class for archiving projects."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the project",
        )
        parser.add_argument(
            "--backup-project-id",
            dest="backup_project_ref_id",
            required=False,
            help="Use this project as a replacement for the archived one in case of match",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        backup_project_ref_id = (
            EntityId.from_raw(args.backup_project_ref_id)
            if args.backup_project_ref_id
            else None
        )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ProjectArchiveArgs(
                ref_id=ref_id, backup_project_ref_id=backup_project_ref_id
            ),
        )
