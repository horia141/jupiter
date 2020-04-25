"""Command for setting the name of a project."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.projects as projects
import repository.workspaces as workspaces
import space_utils
import storage
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class ProjectSetName(command.Command):
    """Command class for setting the name of a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "project-set-name"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the name of a project"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        project_key = basic_validator.project_key_validate_and_clean(args.project_key)
        project_name = basic_validator.entity_name_validate_and_clean(args.name)

        # Load local data

        system_lock = storage.load_lock_file()
        LOGGER.info("Found lock file")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)
        LOGGER.info("Found project file")

        # Apply changes to Notion

        client = NotionClient(token_v2=workspace.token)

        project_root_page = space_utils.find_page_from_space_by_id(
            client, system_lock["projects"][project_key]["root_page_id"])
        LOGGER.info(f"Found the root page via id {project_root_page}")
        project_root_page.title = project_name
        LOGGER.info("Applied changes on Notion")

        # Apply changes locally
        project.name = project_name
        projects_repository.save_project(project)
        LOGGER.info("Applied changes locally")
