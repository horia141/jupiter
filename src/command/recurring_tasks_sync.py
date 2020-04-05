"""Command for syncing the recurring tasks from Notion."""

import logging

from notion.client import NotionClient

import command.command as command
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class RecurringtTasksSync(command.Command):
    """Command class for syncing  projects."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Synchronises Notion and the local storage for recurring tasks"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--prefer", choices=["notion", "local"], default="notion", help="Which source to prefer")
        parser.add_argument("--project", type=str, dest="project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        prefer = args.prefer
        project_key = args.project

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")
        project = storage.load_project(project_key)
        LOGGER.info("Loaded the project data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace["token"])

        # Explore Notion and apply to local

        recurring_tasks_set = {}
        for group in project["recurring_tasks"]["entries"].values():
            for recurring_task in group["tasks"]:
                recurring_tasks_set[recurring_task["ref_id"]] = recurring_task

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["recurring_tasks"]["root_page_id"])
        recurring_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project_key]["recurring_tasks"]["database_view_id"],
                collection=recurring_tasks_page.collection) \
            .build_query() \
            .execute()

        # First, update the recurring tasks collection schema, with the full group
        # structure. We need to do this at the start, so all other operations assume
        # Notion and local are synced wrt this thing and can work easily.
        recurring_tasks_collection = recurring_tasks_page.collection
        recurring_tasks_schema = recurring_tasks_collection.get("schema")
        all_local_groups = {k.lower().strip(): k for k in project["recurring_tasks"]["entries"].keys()}
        all_notion_groups = recurring_tasks_schema[schema.RECURRING_TASKS_GROUP_KEY]
        if "options" not in all_notion_groups:
            all_notion_groups["options"] = []
        all_notion_groups_key = [k["value"].lower().strip() for k in all_notion_groups["options"]]
        for (local_group_key, local_group_value) in all_local_groups.items():
            if local_group_key in all_notion_groups_key:
                continue
            all_notion_groups["options"].append({
                "color": schema.get_stable_color(local_group_key),
                "id": str(uuid.uuid4()),
                "value": schema.format_name_for_option(local_group_value)
            })
        recurring_tasks_collection.set("schema", recurring_tasks_schema)

        # Then look at each recurring task in Notion and try to match it with one in the local storage

        recurring_tasks_row_set = {}
        for recurring_tasks_row in recurring_tasks_rows:
            LOGGER.info(f"Processing {recurring_tasks_row}")
            if recurring_tasks_row.ref_id is None or recurring_tasks_row.ref_id == "":
                # If the recurring task doesn't exist locally, we create it!
                new_recurring_task = {
                    "ref_id": str(project["recurring_tasks"]["next_idx"]),
                    "name": recurring_tasks_row.title,
                    "period": recurring_tasks_row.period,
                    "group": recurring_tasks_row.group,
                    "eisen": recurring_tasks_row.eisen,
                    "difficulty": recurring_tasks_row.difficulty,
                    "due_at_time": recurring_tasks_row.due_at_time,
                    "due_at_day": recurring_tasks_row.due_at_day,
                    "due_at_month": recurring_tasks_row.due_at_month,
                    "suspended": recurring_tasks_row.suspended,
                    "skip_rule": recurring_tasks_row.skip_rule,
                    "must_do": recurring_tasks_row.must_do
                }
                project["recurring_tasks"]["next_idx"] = project["recurring_tasks"]["next_idx"] + 1
                if recurring_tasks_row.group in project["recurring_tasks"]["entries"]:
                    project["recurring_tasks"]["entries"][recurring_tasks_row.group]["tasks"].append(new_recurring_task)
                else:
                    project["recurring_tasks"]["entries"][recurring_tasks_row.group] = {
                        "format": "{name}",
                        "tasks": [new_recurring_task]
                    }
                LOGGER.info(f"Found new recurring task from Notion {recurring_tasks_row.title}")
                recurring_tasks_row.ref_id = new_recurring_task["ref_id"]
                LOGGER.info(f"Applied changes on Notion side too as {recurring_tasks_row}")
                recurring_tasks_set[recurring_tasks_row.ref_id] = new_recurring_task
                recurring_tasks_row_set[recurring_tasks_row.ref_id] = recurring_tasks_row
            elif recurring_tasks_row.ref_id in recurring_tasks_set:
                # If the recurring task exists locally, we sync it with the remote
                recurring_task = recurring_tasks_set[recurring_tasks_row.ref_id]
                if prefer == "notion":
                    # Copy over the parameters from Notion to local
                    LOGGER.error("Case not covered yet")
                elif prefer == "local":
                    # Copy over the parameters from local to Notion
                    recurring_tasks_row.title = recurring_task["name"]
                    recurring_tasks_row.group = recurring_task["group"]
                    recurring_tasks_row.period = recurring_task["period"]
                    setattr(recurring_tasks_row, schema.INBOX_TASK_ROW_EISEN_KEY, recurring_task["eisen"])
                    recurring_tasks_row.difficulty = recurring_task["difficulty"]
                    recurring_tasks_row.due_at_time = recurring_task["due_at_time"]
                    recurring_tasks_row.due_at_day = recurring_task["due_at_day"]
                    recurring_tasks_row.due_at_month = recurring_task["due_at_month"]
                    recurring_tasks_row.must_do = recurring_task["must_do"]
                    recurring_tasks_row.skip_rule = recurring_task["skip_rule"]
                    LOGGER.info(f"Changed recurring task with id={recurring_tasks_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {prefer}")
                recurring_tasks_row_set[recurring_tasks_row.ref_id] = recurring_tasks_row
            else:
                LOGGER.error("Case not covered yet")

        storage.save_project(project_key, project)
        LOGGER.info("Applied local changes")

        # Now, go over each local recurring task, and add it to Notion if it doesn't
        # exist there!

        assert len(recurring_tasks_set) == len(recurring_tasks_row_set)

        # What is now left to do is just update all the inbox tasks according to the new forms of
        # recurring tasks.

        return

        # Apply changes locally

        vacations_set = {v["ref_id"]: v for v in workspace["vacations"]["entries"]}

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        vacations_rows = client \
            .get_collection_view(the_lock["vacations"]["database_view_id"], collection=vacations_page.collection) \
            .build_query() \
            .execute()

        # Explore Notion and apply to local
        vacations_rows_set = {}
        for vacation_row in vacations_rows:
            LOGGER.info(f"Processing {vacation_row}")
            if vacation_row.ref_id is None or vacation_row.ref_id == "":
                # If the vacation doesn't exist locally, we create it:
                new_vacation = {
                    "ref_id": str(workspace["vacations"]["next_idx"]),
                    "name": vacation_row.title,
                    "start_date": vacation_row.start_date.start,
                    "end_date": vacation_row.end_date.start
                }
                if vacation_row.start_date.start >= vacation_row.end_date.start:
                    raise Exception(f"Start date for vacation {vacation_row.title} is after end date")
                workspace["vacations"]["next_idx"] = workspace["vacations"]["next_idx"] + 1
                workspace["vacations"]["entries"].append(new_vacation)
                LOGGER.info(f"Found new vacation from Notion {vacation_row.title}")
                vacation_row.ref_id = new_vacation["ref_id"]
                LOGGER.info(f"Applies changes on Notion side too as {vacation_row}")
                vacations_rows_set[vacation_row.ref_id] = vacation_row
            elif vacation_row.ref_id in vacations_set:
                # If the vacation exists locally, we sync it with the remote:
                if prefer == "notion":
                    vacations_set[vacation_row.ref_id]["name"] = vacation_row.title
                    vacations_set[vacation_row.ref_id]["start_date"] = vacation_row.start_date.start
                    vacations_set[vacation_row.ref_id]["end_date"] = vacation_row.end_date.start
                    if vacation_row.start_date.start >= vacation_row.end_date.start:
                        raise Exception(f"Start date for vacation {vacation_row.title} is after end date")
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from Notion")
                elif prefer == "local":
                    vacation_row.title = vacations_set[vacation_row.ref_id]["name"]
                    vacation_row.start_date = vacations_set[vacation_row.ref_id]["start_date"]
                    vacation_row.end_date = vacations_set[vacation_row.ref_id]["end_date"]
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {prefer}")
                vacations_rows_set[vacation_row.ref_id] = vacation_row
            else:
                # If the vacation is not new, and does not exist on the local side, it means it got removed
                # badly, and we need to redo this.
                vacation_row.remove()
                LOGGER.info(f"Removed vacation with id={vacation_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for vacation in workspace["vacations"]["entries"]:
            if vacation["ref_id"] in vacations_rows_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue

            # If the vacation does not exist on Notion side, we create it.
            new_vacation_row = vacations_page.collection.add_row()
            new_vacation_row.title = vacation["name"]
            new_vacation_row.start_date = vacation["start_date"]
            new_vacation_row.end_date = vacation["end_date"]
            new_vacation_row.ref_id = vacation["ref_id"]
            LOGGER.info(f"Created new vacation on Notion side {new_vacation_row}")

        workspace["vacations"]["entries"] = sorted(
            workspace["vacations"]["entries"], key=lambda vac: vac["start_date"])
        storage.save_workspace(workspace)
        LOGGER.info("Applied local changes")
