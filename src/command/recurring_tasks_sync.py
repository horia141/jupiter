"""Command for syncing the recurring tasks from Notion."""

import logging
import re
import uuid

from notion.client import NotionClient
import pendulum

import command.command as command
import service.workspaces as workspaces
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
        workspace_repository = workspaces.WorkspaceRepository()
        workspace = workspace_repository.load_workspace()
        project = storage.load_project(project_key)
        LOGGER.info("Loaded the project data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

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

                new_recurring_task = self._build_entity_from_row({
                    "ref_id": str(project["recurring_tasks"]["next_idx"])
                }, recurring_tasks_row)

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

                    recurring_task = self._build_entity_from_row(recurring_task, recurring_tasks_row)

                    # Recreate groups structure. Boy. I'll be glad to be rid of this!
                    if old_group != recurring_task["group"]:
                        if recurring_task["group"] in project["recurring_tasks"]["entries"]:
                            project["recurring_tasks"]["entries"][recurring_task["group"]]["tasks"]\
                                .append(recurring_task)
                        else:
                            project["recurring_tasks"]["entries"][recurring_task["group"]] = {
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
                    setattr(recurring_tasks_row, schema.INBOX_TASK_ROW_EISEN_KEY, recurring_task.get("eisen", []))
                    recurring_tasks_row.difficulty = recurring_task.get("difficulty", None)
                    recurring_tasks_row.due_at_time = recurring_task.get("due_at_time", None)
                    recurring_tasks_row.due_at_day = recurring_task.get("due_at_day", None)
                    recurring_tasks_row.due_at_month = recurring_task.get("due_at_month", None)
                    recurring_tasks_row.must_do = recurring_task.get("must_do", False)
                    recurring_tasks_row.skip_rule = recurring_task.get("skip_rule", None)
                    LOGGER.info(f"Changed recurring task with id={recurring_tasks_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {prefer}")
                recurring_tasks_row_set[recurring_tasks_row.ref_id] = recurring_tasks_row
            else:
                LOGGER.info(f"Removed dangling recurring task in Notion {recurring_tasks_row}")
                recurring_tasks_row.remove()

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
            setattr(new_recurring_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, recurring_task.get("eisen", []))
            new_recurring_task_row.difficulty = recurring_task.get("difficulty", None)
            new_recurring_task_row.due_at_time = recurring_task.get("due_at_time", None)
            new_recurring_task_row.due_at_day = recurring_task.get("due_at_day", None)
            new_recurring_task_row.due_at_month = recurring_task.get("due_at_month", None)
            new_recurring_task_row.must_do = recurring_task.get("must_do", False)
            new_recurring_task_row.skip_rule = recurring_task.get("skip_rule", None)
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
            if inbox_task_row.recurring_task_id is None or inbox_task_row.recurring_task_id == "":
                continue
            recurring_task = recurring_tasks_set.get(inbox_task_row.recurring_task_id, None)
            if recurring_task is None:
                # If this is happening, then this is a dangling inbox task. It'll be removed!
                LOGGER.info(f"Removing dangling inbox task {inbox_task_row}")
                inbox_task_row.remove()
                continue
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

    @staticmethod
    def _clean_eisen(eisen):
        if len(eisen) == 0:
            return []
        if len(eisen) == 1 and eisen[0] == '':
            return []
        return eisen

    @staticmethod
    def _build_entity_from_row(entity, row):
        name = row.title.strip()
        group = row.group.strip()
        period = row.period.strip().lower()
        eisen = [e.strip().lower() for e in RecurringtTasksSync._clean_eisen(row.eisen)]
        difficulty = row.difficulty.strip().lower() if row.difficulty else None
        due_at_time = row.due_at_time.strip().lower() if row.due_at_time else None
        due_at_day = row.due_at_day
        due_at_month = row.due_at_month
        must_do = row.must_do
        skip_rule = row.skip_rule.strip().lower() if row.skip_rule else None

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        if len(group) == 0:
            raise Exception("Most provide a non-empty group")

        if len(period) == 0:
            raise Exception("Must provide a non-empty project")
        if period not in [k.lower() for k in schema.INBOX_TIMELINE]:
            raise Exception(f"Invalid period value '{period}'")

        if any(e not in [k.lower() for k in schema.INBOX_EISENHOWER] for e in eisen):
            raise Exception(f"Invalid eisenhower values {eisen}")

        if difficulty:
            if len(difficulty) == 0:
                raise Exception("Must provide a non-empty difficulty")
            if difficulty not in [k.lower() for k in schema.INBOX_DIFFICULTY]:
                raise Exception(f"Invalid difficulty value '{difficulty}")

        if due_at_time:
            if not re.match("^[0-9][0-9]:[0-9][0-9]$", due_at_time):
                raise Exception(f"Invalid due time value '{due_at_time}'")

        entity["name"] = name
        entity["group"] = group
        entity["period"] = period
        entity["eisen"] = eisen
        entity["difficulty"] = difficulty
        entity["due_at_time"] = due_at_time
        entity["due_at_day"] = due_at_day
        entity["due_at_month"] = due_at_month
        entity["must_do"] = must_do
        entity["suspended"] = row.suspended
        entity["skip_rule"] = skip_rule

        return entity
