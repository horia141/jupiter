"""UseCase for showing the projects."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.projects.find import ProjectFindArgs, ProjectFindUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class ProjectShow(LoggedInReadonlyCommand[ProjectFindUseCase]):
    """UseCase class for showing the projects."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--show-archived",
            dest="show_archived",
            default=False,
            action="store_true",
            help="Whether to show archived vacations or not",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ProjectFindArgs(allow_archived=show_archived, filter_ref_ids=None),
        )

        sorted_projects = sorted(
            result.projects,
            key=lambda pe: (pe.archived, pe.created_time),
        )

        rich_tree = Tree("💡 Projects", guide_style="bold bright_blue")

        for project in sorted_projects:
            project_text = Text("")
            project_text.append(entity_id_to_rich_text(project.ref_id))
            project_text.append(" ")
            project_text.append(entity_name_to_rich_text(project.name))

            if project.archived:
                project_text.stylize("gray62")

            rich_tree.add(project_text)

        console = Console()
        console.print(rich_tree)
