"""Command for setting the name of a project."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.projects import ProjectsController
from domain.common.entity_name import EntityName
from domain.projects.project_key import ProjectKey

LOGGER = logging.getLogger(__name__)


class ProjectSetName(command.Command):
    """Command class for setting the name of a project."""

    _projects_controller: Final[ProjectsController]

    def __init__(self, projects_controller: ProjectsController) -> None:
        """Constructor."""
        self._projects_controller = projects_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "projects-set-name"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the name of a project"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = ProjectKey.from_raw(args.project_key)
        project_name = EntityName.from_raw(args.name)
        self._projects_controller.set_project_name(project_key, project_name)
