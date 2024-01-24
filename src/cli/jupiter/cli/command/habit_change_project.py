"""Change the project for a habit."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.habits.change_project import (
    HabitChangeProjectArgs,
    HabitChangeProjectUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class HabitChangeProject(LoggedInMutationCommand[HabitChangeProjectUseCase]):
    """UseCase class for hard removing habits."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="Show only tasks selected by this id",
        )
        project = parser.add_mutually_exclusive_group()
        project.add_argument(
            "--project-id",
            dest="project_ref_id",
            help="The project to reassign this habit to",
        )
        project.add_argument(
            "--clear-project",
            dest="clear_project",
            default=False,
            action="store_const",
            const=True,
            help="Clear the project and use the default one",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_id = EntityId.from_raw(args.ref_id)
        if args.clear_project:
            project_ref_id = None
        else:
            project_ref_id = EntityId.from_raw(args.project_ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            HabitChangeProjectArgs(ref_id=ref_id, project_ref_id=project_ref_id),
        )
