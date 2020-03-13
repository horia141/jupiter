import logging

from notion.client import NotionClient

import commands.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceInit(command.Command):

    @staticmethod
    def name():
        return "ws-init"

    @staticmethod
    def description():
        return "Initialise a workspace"

    def build_parser(self, parser):
        parser.add_argument("--name", required=True, help="The plan name to use")
        parser.add_argument("--token", dest="token", required=True, help="The Notion access token to use")
        parser.add_argument("--space-id", dest="space_id", required=True, help="The Notion space id to use")

    def run(self, args):
        # Load lockfile

        try:
            system_lock = lockfile.load_lock_file()
            LOGGER.info("Found system lock")
        except Exception as e:
            system_lock = lockfile.build_empty_lockfile()
            LOGGER.info("No system lock")

        name = args.name
        token = args.token
        space_id = args.space_id

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=token)
        space = client.get_space(space_id)

        if "root_page_id" in system_lock:
            found_root_page = space_utils.find_page_from_space_by_id(client, system_lock["root_page_id"])
            LOGGER.info(f"Found the root page via id {found_root_page}")
        else:
            LOGGER.info("Attempting to find root page via name in full space")
            found_root_page = space_utils.find_page_from_space_by_name(client, name, space)
            LOGGER.info(f"Found the root page via name {found_root_page}")
        if not found_root_page:
            if not args.dry_run:
                found_root_page = space_utils.create_page_in_space(space, name)
            LOGGER.info(f"Created the root page {found_root_page}")

        if args.dry_run:
            return

        # Apply the changes to the Notion side

        found_root_page.title = name
        LOGGER.info("Applied changes on Notion side")

        # Apply the changes to the local side

        try:
            workspace = storage.load_workspace()
            LOGGER.info("Found workspace config")
        except IOError as e:
            workspace = storage.build_empty_workspace()
            LOGGER.info("No workspace config")

        workspace["space_id"] = space_id
        workspace["name"] = name
        workspace["token"] = token
        storage.save_workspace(workspace)
        LOGGER.info("Applied changes on local side")

        # Save lockfile

        system_lock["root_page_id"] = found_root_page.id
        lockfile.save_lock_file(system_lock)
