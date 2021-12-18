"""Command for creating projects."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from models.framework import UpdateAction
from use_cases.projects.update import ProjectUpdateCommand

LOGGER = logging.getLogger(__name__)


class ProjectUpdate(command.Command):
    """Command class for updating projects."""

    _command: Final[ProjectUpdateCommand]

    def __init__(self, the_command: ProjectUpdateCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "project-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a project"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The key of the project")
        parser.add_argument("--name", dest="name", required=False, help="The name of the project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = ProjectKey.from_raw(args.project_key)
        if args.name is not None:
            project_name = UpdateAction.change_to(EntityName.from_raw(args.name))
        else:
            project_name = UpdateAction.do_nothing()
        self._command.execute(ProjectUpdateCommand.Args(key=project_key, name=project_name))
