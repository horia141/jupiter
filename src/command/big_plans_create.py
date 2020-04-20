"""Command for creating big plans."""

import logging
import uuid

from notion.block import CollectionViewBlock
from notion.client import NotionClient
import pendulum

import command.command as command
import repository.big_plans as big_plans
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class BigPlansCreate(command.Command):
    """Command class for creating big plans."""

    @staticmethod
    def name():
        """The name of the command."""
        return "big-plans-create"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create or update a big plan"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project", required="True",
                            help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the big plan")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        name = args.name.strip()
        due_date = pendulum.parse(args.due_date) if args.due_date else None

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)

        # Apply changes locally

        new_big_plan = big_plans_repository.create_big_plan(
            project_ref_id=project.ref_id, name=name, archived=False, status=big_plans.BigPlanStatus.ACCEPTED,
            due_date=due_date, notion_link_uuid=uuid.uuid4())

        # Apply the changes Notion side

        client = NotionClient(token_v2=workspace.token)

        big_plans_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["big_plan"]["root_page_id"])
        big_plans_collection = big_plans_page.collection

        new_big_plan_row = big_plans_collection.add_row()
        new_big_plan_row.ref_id = new_big_plan.ref_id
        new_big_plan_row.title = name
        new_big_plan_row.status = new_big_plan.status.value
        new_big_plan_row.due_date = new_big_plan.due_date
        new_big_plan_row.archived = False
        setattr(new_big_plan_row, "inbox_id_ref", str(new_big_plan.notion_link_uuid))
        LOGGER.info("Applied Notion changes")

        # Also update the corresponding Inbox's schema for the big plan.

        inbox_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["inbox"]["root_page_id"])
        inbox_collection = inbox_page.collection
        inbox_schema = inbox_collection.get("schema")

        inbox_big_plan_options = [{
            "color": schema.get_stable_color(str(bp.notion_link_uuid)),
            "id": str(bp.notion_link_uuid),
            "value": schema.format_name_for_option(bp.name)
        } for bp in big_plans_repository.list_all_big_plans(filter_parent_ref_id=[project.ref_id])]
        inbox_schema[schema.INBOX_BIGPLAN_KEY]["options"] = inbox_big_plan_options
        inbox_collection.set("schema", inbox_schema)
        LOGGER.info("Updated the schema for the associated inbox")

        # Setup the structure, yo!

        LOGGER.info(f"Creating views structure for plan {new_big_plan_row}")

        new_big_plan_view_block = None
        new_big_plan_view = None

        for big_plan_child in new_big_plan_row.children:
            if not isinstance(big_plan_child, CollectionViewBlock):
                continue

            if big_plan_child.title != "Inbox":
                continue

            new_big_plan_view_block = big_plan_child
            new_big_plan_view = new_big_plan_view_block.views[0]
            LOGGER.info(f"Found already existing inbox tasks view {new_big_plan_view_block}")
            break

        if not new_big_plan_view_block:
            new_big_plan_view_block = new_big_plan_row.children.add_new(CollectionViewBlock)
            new_big_plan_view_block.collection = inbox_collection
            new_big_plan_view = new_big_plan_view_block.views.add_new(view_type="table")
            LOGGER.info(f"Created new view block {new_big_plan_view_block} and view for it {new_big_plan_view}")

        client.submit_transaction([{
            "id": new_big_plan_view.id,
            "table": "collection_view",
            "path": [],
            "command": "update",
            "args": schema.get_view_schema_for_big_plan_desc(
                schema.format_name_for_option(new_big_plan_row.name))
        }])
