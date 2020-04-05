"""Command for syncing the recurring tasks from Notion."""

import logging
import uuid

from notion.client import NotionClient
import pendulum

import command.command as command
import schedules
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)
DONE_STATUS = [schema.DONE_STATUS, schema.NOT_DONE_STATUS]


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
                    old_group = recurring_task["group"]
                    group = recurring_tasks_row.group

                    recurring_task["name"] = recurring_tasks_row.title
                    recurring_task["group"] = recurring_tasks_row.group
                    recurring_task["period"] = recurring_tasks_row.period
                    recurring_task["eisen"] = recurring_tasks_row.eisen
                    recurring_task["difficulty"] = recurring_tasks_row.difficulty
                    recurring_task["due_at_time"] = recurring_tasks_row.due_at_time
                    recurring_task["due_at_day"] = recurring_tasks_row.due_at_day
                    recurring_task["due_at_month"] = recurring_tasks_row.due_at_month
                    recurring_task["must_do"] = recurring_tasks_row.must_do
                    recurring_task["skip_rule"] = recurring_tasks_row.skip_rule

                    # Recreate groups structure. Boy. I'll be glad to be rid of this!
                    if old_group != recurring_task["group"]:
                        if group in project["recurring_tasks"]["entries"]:
                            project["recurring_tasks"]["entries"][group]["tasks"].append(recurring_task)
                        else:
                            project["recurring_tasks"]["entries"][group] = {
                                "format": "{name}",
                                "tasks": [recurring_task]
                            }

                        idx = 0
                        for recurring_task_match in project["recurring_tasks"]["entries"][old_group]["tasks"]:
                            if recurring_task_match["ref_id"] != recurring_task["ref_id"]:
                                idx += 1
                                continue
                            del project["recurring_tasks"]["entries"][old_group]["tasks"][idx]
                            break

                    LOGGER.info(f"Changed recurring task with id={recurring_tasks_row.ref_id} from Notion")
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

        for recurring_task in recurring_tasks_set.values():
            # We've already processed this thing above
            if recurring_task["ref_id"] in recurring_tasks_row_set:
                continue

            new_recurring_task_row = recurring_tasks_collection.add_row()
            new_recurring_task_row.ref_id = recurring_task["ref_id"]
            new_recurring_task_row.title = recurring_task["name"]
            new_recurring_task_row.group = recurring_task["group"]
            new_recurring_task_row.period = recurring_task["period"]
            setattr(new_recurring_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, recurring_task["eisen"])
            new_recurring_task_row.difficulty = recurring_task["difficulty"]
            new_recurring_task_row.due_at_time = recurring_task["due_at_time"]
            new_recurring_task_row.due_at_day = recurring_task["due_at_day"]
            new_recurring_task_row.due_at_month = recurring_task["due_at_month"]
            new_recurring_task_row.must_do = recurring_task["must_do"]
            new_recurring_task_row.skip_rule = recurring_task["skip_rule"]
            LOGGER.info(f'Created Notion task for {recurring_task["name"]}')

        # What is now left to do is just update all the inbox tasks according to the new forms of
        # recurring tasks.

        inbox_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["inbox"]["root_page_id"])
        inbox_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project_key]["inbox"]["database_view_id"],
                collection=inbox_tasks_page.collection) \
            .build_query() \
            .execute()

        for inbox_task_row in inbox_tasks_rows:
            recurring_task = recurring_tasks_set[inbox_task_row.recurring_task_id]
            schedule = schedules.get_schedule(
                recurring_task["period"], recurring_task["name"], pendulum.instance(inbox_task_row.created_date.start),
                recurring_task["skip_rule"], recurring_task["due_at_time"], recurring_task["due_at_day"],
                recurring_task["due_at_month"])
            setattr(inbox_task_row, schema.INBOX_TASK_ROW_DUE_DATE_KEY, schedule.due_time)
            inbox_task_row.title = schedule.full_name
            inbox_task_row.difficulty = recurring_task["difficulty"]
            inbox_task_row.eisen = recurring_task["eisen"]
            if recurring_task not in DONE_STATUS:
                setattr(inbox_task_row, schema.INBOX_TASK_ROW_PERIOD_KEY, schedule.period)
                setattr(inbox_task_row, schema.INBOX_TASK_ROW_TIMELINE_KEY, schedule.timeline)
            LOGGER.info(f"Applied Notion changes to inbox task {inbox_task_row}")
