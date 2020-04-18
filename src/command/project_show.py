"""Command for showing the projects."""

import logging

import command.command as command
import service.projects as projects

LOGGER = logging.getLogger(__name__)


class ProjectShow(command.Command):
    """Command class for showing the projects."""

    @staticmethod
    def name():
        """The name of the command."""
        return "project-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the projects"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project", help="The project key to show")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project

        # Load local storage

        LOGGER.info("Loaded the system lock")
        projects_repository = projects.ProjectsRepository()

        if project_key:
            # Print details about a single project
            project = projects_repository.load_project_by_key(project_key)
            LOGGER.info("Loaded the project data")
            print(f'{project_key}: {project.name}')
        else:
            # Print a summary of all projects
            for project in projects_repository.list_all_projects():
                print(f'{project.key}: {project.name}')
