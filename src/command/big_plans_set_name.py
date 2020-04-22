"""Command for setting the name of a big plan."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.big_plans as big_plans
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class BigPlansSetName(command.Command):
    """Command class for setting the name of a big plan."""

    @staticmethod
    def name():
        """The name of the command."""
        return "big-plans-set-name"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the name of a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--name", dest="name", required=True, help="The name of the big plan")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        name = args.name.strip()

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        # Apply changes locally

        workspace = workspace_repository.load_workspace()

        big_plan = big_plans_repository.load_big_plan_by_id(ref_id)
        big_plan.set_name(name)
        big_plans_repository.save_big_plan(big_plan)

        project = projects_repository.load_project_by_id(big_plan.project_ref_id)

        # Apply changes in Notion

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # First, change the recurring task entry

        big_plans_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["big_plan"]["root_page_id"])
        big_plans_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["big_plan"]["database_view_id"],
                collection=big_plans_page.collection) \
            .build_query() \
            .execute()

        big_plan_row = next(r for r in big_plans_rows if r.ref_id == ref_id)
        big_plan_row.title = big_plan.name
        LOGGER.info("Applied Notion changes")

        # Also update the corresponding Inbox's schema for the big plan.

        inbox_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["inbox"]["root_page_id"])
        inbox_collection = inbox_page.collection
        inbox_schema = inbox_collection.get("schema")

        inbox_big_plan_options = [{
            "color": schema.get_stable_color(str(bp.notion_link_uuid)),
            "id": str(bp.notion_link_uuid),
            "value": schema.format_name_for_option(bp.name)
        } for bp in big_plans_repository.list_all_big_plans(filter_project_ref_id=[project.ref_id])]
        inbox_schema[schema.INBOX_BIGPLAN_KEY]["options"] = inbox_big_plan_options
        inbox_collection.set("schema", inbox_schema)
        LOGGER.info("Updated the schema for the associated inbox")
