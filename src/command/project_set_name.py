"""Command for setting the name of a project."""

import logging

from notion.client import NotionClient

import command.command as command
import space_utils
import storage

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
        parser.add_argument("project", help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        project_name = args.name

        system_lock = storage.load_lock_file()
        LOGGER.info("Found lock file")
        workspace = storage.load_workspace()
        LOGGER.info("Found workspace file")
        project = storage.load_project(project_key)
        LOGGER.info("Found project file")

        # Apply changes to Notion

        client = NotionClient(token_v2=workspace["token"])

        if project_key in system_lock["projects"]:
            project_lock = system_lock["projects"][project_key]
            LOGGER.info("Project already in system lock")
        else:
            project_lock = {}
            LOGGER.info("Project not in system lock")

        project_root_page = space_utils.find_page_from_space_by_id(client, project_lock["root_page_id"])
        LOGGER.info(f"Found the root page via id {project_root_page}")
        project_root_page.title = project_name
        LOGGER.info("Applied changes on Notion")

        # Apply changes locally
        project["name"] = project_name
        storage.save_project(project_key, project)
        LOGGER.info("Applied changes locally")
