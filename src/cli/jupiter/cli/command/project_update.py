"""UseCase for creating projects."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.projects.update import (
    ProjectUpdateArgs,
    ProjectUpdateUseCase,
)


class ProjectUpdate(LoggedInMutationCommand[ProjectUpdateUseCase]):
    """UseCase class for updating projects."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the project",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            help="The name of the project",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name is not None:
            project_name = UpdateAction.change_to(ProjectName.from_raw(args.name))
        else:
            project_name = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ProjectUpdateArgs(ref_id=ref_id, name=project_name),
        )
