"""Command for updating big plans for a project."""

import hashlib
import logging
import uuid

from notion.block import CollectionViewBlock
from notion.client import NotionClient

import command.command as command
import schema
import storage

LOGGER = logging.getLogger(__name__)


class BigPlansSync(command.Command):
    """Command class for updating big plans for a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "big-plans-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Upsert big plans"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        dry_run = args.dry_run

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace = storage.load_workspace()
        LOGGER.info("Found workspace file")

        _ = storage.load_project(project_key)
        LOGGER.info("Found project file")

        client = NotionClient(token_v2=workspace["token"])

        project_lock = system_lock["projects"][project_key]

        inbox_collection = client.get_block(project_lock["inbox"]["root_page_id"]).collection
        inbox_schema = inbox_collection.get("schema")
        big_plan_collection = client.get_block(project_lock["big_plan"]["root_page_id"]).collection

        inbox_big_plan_options = {}

        for big_plan in big_plan_collection.get_rows():
            LOGGER.info(f"Creating field link for plan {big_plan}")
            option_uuid = getattr(big_plan, schema.BIG_PLAN_TASK_INBOX_ID_KEY, None)
            if option_uuid:
                LOGGER.info(f"Found already existing option id {option_uuid}")
            else:
                LOGGER.info("Will need to create new option id")
                option_uuid = str(uuid.uuid4())
            setattr(big_plan, schema.BIG_PLAN_TASK_INBOX_ID_KEY, option_uuid)
            inbox_big_plan_options[option_uuid] = {
                "color": BigPlansSync._get_stable_color(option_uuid),
                "id": option_uuid,
                "value": BigPlansSync._format_name(big_plan.name)
            }

        inbox_schema[schema.INBOX_BIGPLAN_KEY]["options"] = list(inbox_big_plan_options.values())
        if not dry_run:
            inbox_collection.set("schema", inbox_schema)
            LOGGER.info("Updated the schema for the associated inbox")

        for big_plan in big_plan_collection.get_rows():
            LOGGER.info(f"Creating views structure for plan {big_plan}")

            big_plan_view_block = None
            big_plan_view = None

            for big_plan_child in big_plan.children:
                if not isinstance(big_plan_child, CollectionViewBlock):
                    continue

                if big_plan_child.title != "Inbox":
                    continue

                big_plan_view_block = big_plan_child
                big_plan_view = big_plan_view_block.views[0]
                LOGGER.info(f"Found already existing inbox tasks view {big_plan_view_block}")
                break

            if not dry_run:
                if not big_plan_view_block:
                    big_plan_view_block = big_plan.children.add_new(CollectionViewBlock)
                    big_plan_view_block.collection = inbox_collection
                    big_plan_view = big_plan_view_block.views.add_new(view_type="table")
                    LOGGER.info(f"Created new view block {big_plan_view_block} and view for it {big_plan_view}")

                client.submit_transaction([{
                    "id": big_plan_view.id,
                    "table": "collection_view",
                    "path": [],
                    "command": "update",
                    "args": schema.get_view_schema_for_big_plan_desc(BigPlansSync._format_name(big_plan.name))
                }])

    @staticmethod
    def _get_stable_color(option_id):
        return schema.COLORS[hashlib.sha256(option_id.encode("utf-8")).digest()[0] % len(schema.COLORS)]

    @staticmethod
    def _format_name(big_plan_name):
        output = ""
        for char in big_plan_name:
            if char.isalnum() or char == " ":
                output += char
        return output
