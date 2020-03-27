"""Command for removing a project."""

import logging
from pathlib import Path

from notion.client import NotionClient
import yaml

import command.command as command
import lockfile
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
        parser.add_argument("tasks", help="The tasks file")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        # Load local storage

        workspace = storage.load_workspace()
        LOGGER.info("Found system lock")

        system_lock = lockfile.load_lock_file()
        LOGGER.info("Found system lock")

        with open(args.tasks, "r") as tasks_file:
            tasks = yaml.safe_load(tasks_file)

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=workspace["token"])

        # Apply the changes on Notion side

        key = tasks["key"]

        if key in system_lock["projects"]:
            project_lock = system_lock["projects"][key]
            LOGGER.info("Project already in system lock")
        else:
            project_lock = {}
            LOGGER.info("Project not in system lock")

        project_root_page = space_utils.find_page_from_space_by_id(client, project_lock["root_page_id"])
        LOGGER.info(f"Found the root page via id {project_root_page}")

        project_root_page.remove()

        # Apply the changes to the local side
        del system_lock["projects"][key]
        lockfile.save_lock_file(system_lock)

        path = Path(args.tasks)
        path.unlink()
