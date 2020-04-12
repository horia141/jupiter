"""Command for syncing the projects from Notion."""

import logging

from notion.client import NotionClient

import command.command as command
import service.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class ProjectSync(command.Command):
    """Command class for syncing the projects from Notion."""

    @staticmethod
    def name():
        """The name of the command."""
        return "project-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Synchronises Notion and the local storage"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--prefer", choices=["notion", "local"], default="notion", help="Which source to prefer")
        parser.add_argument("--project", dest="project", required=True, help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        prefer = args.prefer
        project_key = args.project

        # Load local storage

        system_lock = storage.load_lock_file()
        workspace_repository = workspaces.WorkspaceRepository()
        workspace = workspace_repository.load_workspace()
        project = storage.load_project(project_key)
        LOGGER.info("Found project file")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        project_root_page = space_utils.find_page_from_space_by_id(
            client, system_lock["projects"][project_key]["root_page_id"])
        LOGGER.info(f"Found the root page via id {project_root_page}")

        if prefer == "local":
            project_root_page.title = project["name"]
            LOGGER.info("Applied changes to Notion")
        elif prefer == "notion":
            project["name"] = project_root_page.title
            storage.save_project(project_key, project)
            LOGGER.info("Applied local change")
        else:
            raise Exception(f"Invalid preference {prefer}")
