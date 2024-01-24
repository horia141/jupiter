"""UseCase for creating projects."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.projects.create import (
    ProjectCreateArgs,
    ProjectCreateUseCase,
)


class ProjectCreate(LoggedInMutationCommand[ProjectCreateUseCase]):
    """UseCase class for creating projects."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the project",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        project_name = ProjectName.from_raw(args.name)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ProjectCreateArgs(name=project_name),
        )
