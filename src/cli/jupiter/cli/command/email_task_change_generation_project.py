"""UseCase for updating the email task generation project."""
from argparse import ArgumentParser, Namespace
from typing import Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.push_integrations.email.change_generation_project import (
    EmailTaskChangeGenerationProjectArgs,
    EmailTaskChangeGenerationProjectUseCase,
)


class EmailTaskChangeGenerationProject(
    LoggedInMutationCommand[EmailTaskChangeGenerationProjectUseCase]
):
    """Use case for updating the email task generation project."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "email-task-change-generation-project"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the generation project for email tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        generation_project_group = parser.add_mutually_exclusive_group()
        generation_project_group.add_argument(
            "--generation-project-id",
            dest="generation_project_ref_id",
            required=False,
            help="The project key to generate generation tasks",
        )
        generation_project_group.add_argument(
            "--clear-generation-project",
            dest="clear_generation_project",
            required=False,
            default=False,
            action="store_const",
            const=True,
            help="Clear the generation project",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        generation_project_ref_id: Optional[EntityId]
        if args.clear_generation_project:
            generation_project_ref_id = None
        else:
            generation_project_ref_id = EntityId.from_raw(
                args.generation_project_ref_id
            )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            EmailTaskChangeGenerationProjectArgs(
                generation_project_ref_id=generation_project_ref_id,
            ),
        )
