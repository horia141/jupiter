import logging

from notion.client import NotionClient

import commands.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceSetToken(command.Command):

    @staticmethod
    def name():
        return "ws-set-token"

    @staticmethod
    def description():
        return "Change the Notion access token of the workspace"

    def build_parser(self, parser):
        parser.add_argument("token", help="The plan name to use")

    def run(self, args):

        # Argument parsing

        token = args.token

        # Load local storage

        system_lock = lockfile.load_lock_file()
        LOGGER.info("Loaded lockfile")
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        if args.dry_run:
            return

        # Apply the changes to the local side

        workspace["token"] = token
        storage.save_workspace(workspace)
        LOGGER.info("Applied changes on local side")
