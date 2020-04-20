"""Command for archiving a big plan."""

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


class BigPlansArchive(command.Command):
    """Command class for archiving a big plan."""

    @staticmethod
    def name():
        """The name of the command."""
        return "big-plans-archive"

    @staticmethod
    def description():
        """The description of the command."""
        return "Archive a big plan"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required="True", help="The if of the big plan")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        # Parse arguments

        ref_id = args.ref_id

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        big_plans_repository = big_plans.BigPlansRepository()
        projects_repository = projects.ProjectsRepository()

        workspace = workspace_repository.load_workspace()

        big_plan = big_plans_repository.load_big_plan_by_id(ref_id)
        big_plans_repository.remove_big_plan(ref_id)

        project = projects_repository.load_project_by_id(big_plan.project_ref_id)
        LOGGER.info("Applied local changes")

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=workspace.token)

        # Apply the changes on Notion side

        big_plans_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["big_plan"]["root_page_id"])
        big_plans_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["big_plan"]["database_view_id"],
                collection=big_plans_page.collection) \
            .build_query() \
            .execute()

        recurring_task_row = next(r for r in big_plans_rows if r.ref_id == ref_id)
        recurring_task_row.archived = True
        LOGGER.info("Removed recurring task from Notion")

        # Also update the corresponding Inbox's schema for the big plan.

        inbox_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["inbox"]["root_page_id"])
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
