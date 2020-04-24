"""Command for updating big plans for a project."""

import logging
import uuid
from typing import Dict

import pendulum
from notion.block import CollectionViewBlock
from notion.client import NotionClient

import command.command as command
from repository.common import RefId
import repository.big_plans as big_plans
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import space_utils
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
        parser.add_argument("--prefer", choices=["notion", "local"], default="notion", help="Which source to prefer")
        parser.add_argument("--project", dest="project", required="True",
                            help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        prefer = args.prefer
        project_key = args.project

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)
        all_big_plans = big_plans_repository.list_all_big_plans(filter_project_ref_id=[project.ref_id])
        all_big_plans_set: Dict[RefId, big_plans.BigPlan] = {rt.ref_id: rt for rt in all_big_plans}

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Explore Notion and apply to local

        big_plans_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["big_plan"]["root_page_id"])
        big_plans_collection = big_plans_page.collection
        big_plans_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["big_plan"]["database_view_id"],
                collection=big_plans_page.collection) \
            .build_query() \
            .execute()

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        big_plans_row_set = {}
        for big_plan_row in big_plans_rows:
            LOGGER.info(f"Processing {big_plan_row}")
            if big_plan_row.ref_id is None or big_plan_row.ref_id == "":
                # If the big plan doesn't exist locally, we create it!

                new_big_plan_raw = self._build_entity_from_row(big_plan_row)
                new_big_plan = big_plans_repository.create_big_plan(
                    project_ref_id=project.ref_id,
                    name=new_big_plan_raw["name"],
                    archived=new_big_plan_raw["archived"],
                    status=new_big_plan_raw["status"],
                    due_date=new_big_plan_raw["due_date"],
                    notion_link_uuid=uuid.uuid4())

                LOGGER.info(f"Found new big plan from Notion {big_plan_row.title}")
                big_plan_row.ref_id = new_big_plan.ref_id
                setattr(big_plan_row, "inbox_id_ref", str(new_big_plan.notion_link_uuid))
                all_big_plans_set[big_plan_row.ref_id] = new_big_plan
                big_plans_row_set[big_plan_row.ref_id] = big_plan_row
            elif big_plan_row.ref_id in all_big_plans_set:
                # If the big plan exists locally, we sync it with the remote
                big_plan = all_big_plans_set[big_plan_row.ref_id]
                if prefer == "notion":
                    # Copy over the parameters from Notion to local
                    big_plan_raw = self._build_entity_from_row(big_plan_row)
                    big_plan.name = big_plan_raw["name"]
                    big_plan.archived = big_plan_raw["archived"]
                    big_plan.status = big_plan_raw["status"]
                    big_plan.due_date = big_plan_raw["due_date"]
                    # Not updating inbox_id_ref
                    big_plans_repository.save_big_plan(big_plan)
                    LOGGER.info(f"Changed big plan with id={big_plan_row.ref_id} from Notion")
                elif prefer == "local":
                    # Copy over the parameters from local to Notion
                    big_plan_row.title = big_plan.name
                    big_plan_row.archived = big_plan.archived
                    big_plan_row.status = big_plan.status
                    big_plan_row.due_date = big_plan.due_date
                    setattr(big_plan_row, "inbox_id_ref", str(big_plan.notion_link_uuid))
                    LOGGER.info(f"Changed big plan with id={big_plan_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {prefer}")
                big_plans_row_set[big_plan_row.ref_id] = big_plan_row
            else:
                LOGGER.info(f"Removed dangling big plan in Notion {big_plan_row}")
                big_plan_row.remove()

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for big_plan in all_big_plans_set.values():
            # We've already processed this thing above
            if big_plan.ref_id in big_plans_row_set:
                continue

            new_big_plan_row = big_plans_collection.add_row()
            new_big_plan_row.ref_id = big_plan.ref_id
            new_big_plan_row.archived = big_plan.archived
            new_big_plan_row.status = big_plan.status
            new_big_plan_row.due_date = big_plan.due_date
            setattr(new_big_plan_row, "inbox_id_ref", str(big_plan.notion_link_uuid))
            LOGGER.info(f'Created Notion task for {big_plan["name"]}')

        # Also update the corresponding Inbox's schema for the big plan.

        inbox_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["inbox"]["root_page_id"])
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

        # OK, not setup view structure!

        for big_plan_row in big_plans_row_set.values():
            LOGGER.info(f"Creating views structure for plan {big_plan_row}")

            big_plan_view_block = None
            big_plan_view = None

            for big_plan_child in big_plan_row.children:
                if not isinstance(big_plan_child, CollectionViewBlock):
                    continue

                if big_plan_child.title != "Inbox":
                    continue

                big_plan_view_block = big_plan_child
                big_plan_view = big_plan_view_block.views[0]
                LOGGER.info(f"Found already existing inbox tasks view {big_plan_view_block}")
                break

            if not big_plan_view_block:
                big_plan_view_block = big_plan_row.children.add_new(CollectionViewBlock)
                big_plan_view_block.collection = inbox_collection
                big_plan_view = big_plan_view_block.views.add_new(view_type="table")
                LOGGER.info(f"Created new view block {big_plan_view_block} and view for it {big_plan_view}")

            client.submit_transaction([{
                "id": big_plan_view.id,
                "table": "collection_view",
                "path": [],
                "command": "update",
                "args": schema.get_view_schema_for_big_plan_desc(
                    schema.format_name_for_option(big_plan_row.name))
                }])

    @staticmethod
    def _build_entity_from_row(row):
        name = row.title.strip()
        archived = row.archived
        status = big_plans.BigPlanStatus("-".join(f.lower() for f in row.status.strip().split(" "))) \
            if row.status else big_plans.BigPlanStatus.NOT_STARTED
        due_date = row.due_date.start if row.due_date else None

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        entity = {
            "name": name,
            "archived": archived,
            "status": status,
            "due_date": pendulum.parse(str(due_date)) if due_date else None
        }

        return entity
