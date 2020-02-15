import logging

from notion.client import NotionClient
import yaml

import command
import lockfile
import space_utils

LOGGER = logging.getLogger(__name__)

class Init(command.Command):

    @staticmethod
    def name():
        return "init"

    @staticmethod
    def description():
        return "Initialise the system"

    def build_parser(self, parser):
        parser.add_argument("user", help="The user file")

    def run(self, args):
        try:
            system_lock = lockfile.get_lock_file()
            LOGGER.info("Found system lock")
        except Exception as e:
            system_lock = {
                "projects": {}
            }
            LOGGER.info("No system lock")

        with open(args.user, "r") as user_file:
            user = yaml.load(user_file)

        client = NotionClient(token_v2=user["token_v2"])
        space = client.get_space(user["space_id"])
        name = user["name"]

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

        if not args.dry_run:
            system_lock["root_page_id"] = found_root_page.id
            lockfile.save_lock_file(system_lock)
