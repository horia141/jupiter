"""Command for syncing the workspace info from Notion."""

import logging

from notion.client import NotionClient

import command.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceSync(command.Command):
    """Command class for syncing the workspace info from Notion."""

    @staticmethod
    def name():
        """The name of the command."""
        return "ws-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Synchronises Notion and the local storage"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--prefer", choices=["notion", "local"], default="notion", help="Which source to prefer")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        prefer = args.prefer

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

        if prefer == "notion":
            name = found_root_page.title
            workspace["name"] = name
            storage.save_workspace(workspace)
            LOGGER.info("Applied changes on local side")
        elif prefer == "local":
            found_root_page.title = workspace["name"]
            LOGGER.info("Applied changes on Notion side")
        else:
            raise Exception(f"Invalid preference {prefer}")
