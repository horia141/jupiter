"""Command for showing the projects."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.projects import ProjectsController
from domain.projects.project_key import ProjectKey

LOGGER = logging.getLogger(__name__)


class ProjectShow(command.Command):
    """Command class for showing the projects."""

    _projects_controller: Final[ProjectsController]

    def __init__(self, projects_controller: ProjectsController) -> None:
        """Constructor."""
        self._projects_controller = projects_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "projects-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the projects"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="The project key to show")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_keys = [ProjectKey.from_raw(pk) for pk in args.project_keys] if len(args.project_keys) > 0 else None
        response = self._projects_controller.load_all_projects(filter_project_keys=project_keys)

        for project_entry in response.projects:
            project = project_entry.project
            print(f'{project.key}: {project.name}')
