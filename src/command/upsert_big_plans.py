"""Command for updating big plans for a project."""

import hashlib
import logging
import uuid

from notion.block import CollectionViewBlock
from notion.client import NotionClient
import yaml

import command.command as command
import lockfile
import schema
import storage

LOGGER = logging.getLogger(__name__)


class UpsertBigPlans(command.Command):
    """Command class for updating big plans for a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "upsert-big-plans"

    @staticmethod
    def description():
        """The description of the command."""
        return "Upsert big plans"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("tasks", help="The tasks file")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        workspace = storage.load_workspace()

        with open(args.tasks, "r") as tasks_file:
            tasks = yaml.safe_load(tasks_file)

        client = NotionClient(token_v2=workspace["token"])

        self._upsert_big_plans(client, tasks, args.dry_run)

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

    @staticmethod
    def _upsert_big_plans(client, tasks, dry_run):
        key = tasks["key"]

        system_lock = lockfile.load_lock_file()
        project_lock = system_lock["projects"][key]

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
                "color": UpsertBigPlans._get_stable_color(option_uuid),
                "id": option_uuid,
                "value": UpsertBigPlans._format_name(big_plan.name)
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
                    "args": schema.get_view_schema_for_big_plan_desc(UpsertBigPlans._format_name(big_plan.name))
                }])
