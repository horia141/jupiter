"""Command for setting the name of a workspace"""

import logging

from notion.client import NotionClient

import command.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceSetName(command.Command):

    @staticmethod
    def name():
        return "ws-set-name"

    @staticmethod
    def description():
        return "Change the name of the workspace"

    def build_parser(self, parser):
        parser.add_argument("name", help="The plan name to use")

    def run(self, args):

        # Argument parsing

        name = args.name

        # Load local storage

        system_lock = lockfile.load_lock_file()
        LOGGER.info("Loaded lockfile")
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Load Notion storage

        client = NotionClient(token_v2=workspace["token"])
        LOGGER.info("Connected to Notion")
        found_root_page = space_utils.find_page_from_space_by_id(client, system_lock["root_page"]["root_page_id"])
        LOGGER.info(f"Found the root page via id {found_root_page}")

        if args.dry_run:
            return

        # Apply the changes to the Notion side

        found_root_page.title = name
        LOGGER.info("Applied changes on Notion side")

        # Apply the changes to the local side

        workspace["name"] = name
        storage.save_workspace(workspace)
        LOGGER.info("Applied changes on local side")
