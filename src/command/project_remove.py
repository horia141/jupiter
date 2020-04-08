"""Command for removing a project."""

import logging

from notion.client import NotionClient

import command.command as command
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class ProjectRemove(command.Command):
    """Command class for remove a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "project-remove"

    @staticmethod
    def description():
        """The description of the command."""
        return "Remove a project"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        # Parse arguments

        project_key = args.project

        # Load local storage

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace = storage.load_workspace()
        LOGGER.info("Found workspace file")

        _ = storage.load_project(project_key)
        LOGGER.info("Found project file")

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=workspace["token"])

        # Apply the changes on Notion side

        if project_key in system_lock["projects"]:
            project_lock = system_lock["projects"][project_key]
            LOGGER.info("Project already in system lock")
        else:
            project_lock = {}
            LOGGER.info("Project not in system lock")

        project_root_page = space_utils.find_page_from_space_by_id(client, project_lock["root_page_id"])
        LOGGER.info(f"Found the root page via id {project_root_page}")

        project_root_page.remove()
        LOGGER.info("Removed Notion structures")

        # Apply the changes to the local side
        del system_lock["projects"][project_key]
        storage.save_lock_file(system_lock)
        LOGGER.info("Removed from lockfile")

        storage.remove_project(project_key)
        LOGGER.info("Removed project storage")
