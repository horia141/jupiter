"""Command for showing the projects."""

import logging

import command.command as command
import storage

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

        _ = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")
        # Dump out contents of the projects

        if project_key:
            # Print details about a single project
            project = storage.load_project(project_key)
            LOGGER.info("Loaded the project data")
            print(f'{project_key}: {project["name"]}')
        else:
            # Print a summary of all projects
            for project_key in workspace["projects"]:
                project = storage.load_project(project_key)
                print(f'{project_key}: {project["name"]}')
