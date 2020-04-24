"""Command for syncing the inbox tasks for a project."""

import logging
from typing import Dict

import pendulum
from notion.client import NotionClient

import command.command as command
from repository.common import RefId, TaskEisen, TaskDifficulty
import repository.big_plans as big_plans
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks
import repository.workspaces as workspaces
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class InboxTasksSync(command.Command):
    """Command class for syncing the inbox tasks for a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "inbox-tasks-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Sync the inbox tasks for a project between the local store and Notion"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--prefer", choices=["notion", "local"], default="notion", help="Which source to prefer")
        parser.add_argument("--project", dest="project", required="True",
                            help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        prefer = args.prefer
        project_key = args.project
        right_now = pendulum.now()

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)
        all_big_plans_set: Dict[str, big_plans.BigPlan] =\
            {schema.format_name_for_option(bp.name): bp
             for bp in big_plans_repository.list_all_big_plans(filter_project_ref_id=[project.ref_id])}
        all_inbox_tasks = inbox_tasks_repository.list_all_inbox_tasks(filter_project_ref_id=[project.ref_id])
        all_inbox_tasks_set: Dict[RefId, inbox_tasks.InboxTask] = {rt.ref_id: rt for rt in all_inbox_tasks}

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Explore Notion and apply to local

        inbox_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["inbox"]["root_page_id"])
        inbox_tasks_collection = inbox_tasks_page.collection
        inbox_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["inbox"]["database_view_id"],
                collection=inbox_tasks_page.collection) \
            .build_query() \
            .execute()

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        inbox_tasks_row_set = {}
        for inbox_task_row in inbox_tasks_rows:
            LOGGER.info(f"Processing {inbox_task_row}")

            inbox_task_raw = self._build_entity_from_row(inbox_task_row)

            big_plan = None
            recurring_task = None
            if inbox_task_raw["big_plan_ref_id"]:
                big_plan = big_plans_repository.load_big_plan_by_id(inbox_task_raw["big_plan_ref_id"])
            elif inbox_task_raw["big_plan"]:
                big_plan = all_big_plans_set[schema.format_name_for_option(inbox_task_raw["big_plan"])]
            elif inbox_task_raw["recurring_task_ref_id"]:
                recurring_task = recurring_tasks_repository. \
                    load_recurring_task_by_id(inbox_task_raw["recurring_task_ref_id"])

            if inbox_task_row.ref_id is None or inbox_task_row.ref_id == "":
                # If the big plan doesn't exist locally, we create it!
                new_inbox_task = inbox_tasks_repository.create_inbox_task(
                    project_ref_id=project.ref_id,
                    big_plan_ref_id=big_plan.ref_id if big_plan else None,
                    recurring_task_ref_id=recurring_task.ref_id if recurring_task else None,
                    created_date=right_now,
                    name=inbox_task_raw["name"],
                    archived=inbox_task_raw["archived"],
                    status=inbox_task_raw["status"],
                    eisen=inbox_task_raw["eisen"],
                    difficulty=inbox_task_raw["difficulty"],
                    due_date=inbox_task_raw["due_date"],
                    recurring_task_timeline=inbox_task_raw["recurring_task_timeline"])

                LOGGER.info(f"Found new inbox task from Notion {inbox_task_row.title}")
                inbox_task_row.ref_id = new_inbox_task.ref_id
                inbox_task_row.big_plan_id = big_plan.ref_id if big_plan else None
                inbox_task_row.status = new_inbox_task.status.for_notion()
                inbox_task_row.recurring_task_id = recurring_task.ref_id if recurring_task else None
                all_inbox_tasks_set[inbox_task_row.ref_id] = new_inbox_task
                inbox_tasks_row_set[inbox_task_row.ref_id] = inbox_task_row
            elif inbox_task_row.ref_id in all_inbox_tasks_set:
                # If the big plan exists locally, we sync it with the remote
                inbox_task = all_inbox_tasks_set[inbox_task_row.ref_id]
                if prefer == "notion":
                    # Copy over the parameters from Notion to local
                    inbox_task.big_plan_ref_id = big_plan.ref_id if big_plan else None
                    inbox_task.name = inbox_task_raw["name"]
                    inbox_task.archived = inbox_task_raw["archived"]
                    inbox_task.status = inbox_task_raw["status"]
                    inbox_task.eisen = inbox_task_raw["eisen"]
                    inbox_task.difficulty = inbox_task_raw["difficulty"]
                    inbox_task.due_date = inbox_task_raw["due_date"]
                    # Not updating inbox_id_ref
                    inbox_tasks_repository.save_inbox_task(inbox_task)
                    LOGGER.info(f"Changed inbox task with id={inbox_task_row.ref_id} from Notion")
                elif prefer == "local":
                    # Copy over the parameters from local to Notion
                    inbox_task_row.big_plan_id = inbox_task.big_plan_ref_id
                    inbox_task_row.big_plan = schema.format_name_for_option(big_plan.name) if big_plan else None
                    inbox_task_row.recurring_task_id = inbox_task.recurring_task_ref_id
                    inbox_task_row.created_date = inbox_task.created_date
                    inbox_task_row.title = inbox_task.name
                    inbox_task_row.archived = inbox_task.archived
                    inbox_task_row.status = inbox_task.status.for_notion()
                    setattr(inbox_task_row, "eisenhower", [e.value for e in inbox_task.eisen])
                    inbox_task_row.difficulty = inbox_task.difficulty.value if inbox_task.difficulty else None
                    inbox_task_row.due_date = inbox_task.due_date
                    inbox_task_row.recurring_timeline = inbox_task.recurring_task_timeline
                    LOGGER.info(f"Changed inbox task with id={inbox_task_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {prefer}")
                inbox_tasks_row_set[inbox_task_row.ref_id] = inbox_task_row
            else:
                LOGGER.info(f"Removed dangling big plan in Notion {inbox_task_row}")
                inbox_task_row.remove()

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for inbox_task in all_inbox_tasks_set.values():
            # We've already processed this thing above
            if inbox_task.ref_id in inbox_tasks_row_set:
                continue

            big_plan = None
            if inbox_task.big_plan_ref_id:
                big_plan = big_plans_repository.load_big_plan_by_id(inbox_task.big_plan_ref_id)
            elif inbox_task.recurring_task_ref_id:
                recurring_task = recurring_tasks_repository\
                    .load_recurring_task_by_id(inbox_task.recurring_task_ref_id)

            new_inbox_task_row = inbox_tasks_collection.add_row()
            new_inbox_task_row.ref_id = inbox_task.ref_id
            if big_plan:
                new_inbox_task_row.big_plan_id = inbox_task.big_plan_ref_id
                new_inbox_task_row.big_plan = schema.format_name_for_option(big_plan.name)
            if recurring_task:
                new_inbox_task_row.recurring_task_id = inbox_task.recurring_task_ref_id
            new_inbox_task_row.recurring_task_id = None
            new_inbox_task_row.created_date = new_inbox_task.created_date
            new_inbox_task_row.title = new_inbox_task.name
            new_inbox_task_row.archived = False
            new_inbox_task_row.status = new_inbox_task.status.value
            setattr(new_inbox_task_row, "eisenhower", [e.value for e in new_inbox_task.eisen])
            setattr(
                new_inbox_task_row, "difficulty",
                new_inbox_task.difficulty.value if new_inbox_task.difficulty else None)
            new_inbox_task_row.due_date = new_inbox_task.due_date
            setattr(new_inbox_task_row, "from_script", True)
            setattr(new_inbox_task_row, "recurring_period", recurring_task.period.value)
            new_inbox_task_row.recurring_timeline = inbox_task.recurring_task_timeline
            LOGGER.info(f'Created Notion inbox task for {inbox_task["name"]}')

    @staticmethod
    def _build_entity_from_row(row):
        big_plan_ref_id = row.big_plan_id if (row.big_plan_id is not None and row.big_plan_id != '') else None
        big_plan = row.big_plan if (row.big_plan is not None and row.big_plan != '') else None
        recurring_task_ref_id = row.recurring_task_id
        name = row.title.strip()
        archived = row.archived
        status = inbox_tasks.InboxTaskStatus("-".join(f.lower() for f in row.status.strip().split(" ")))\
            if row.status else inbox_tasks.InboxTaskStatus.NOT_STARTED
        eisen = [TaskEisen(e.strip().lower()) for e in InboxTasksSync._clean_eisen(row.eisen)]
        difficulty = TaskDifficulty(row.difficulty.strip().lower()) if row.difficulty else None
        due_date = row.due_date.start if row.due_date else None
        recurring_task_timeline = row.recurring_timeline

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        entity = {
            "big_plan_ref_id": big_plan_ref_id,
            "big_plan": big_plan,
            "recurring_task_ref_id": recurring_task_ref_id,
            "name": name,
            "archived": archived,
            "status": status,
            "eisen": eisen,
            "difficulty": difficulty,
            "due_date": pendulum.parse(str(due_date)) if due_date else None,
            "recurring_task_timeline": recurring_task_timeline
        }

        return entity

    @staticmethod
    def _clean_eisen(eisen):
        if len(eisen) == 0:
            return []
        if len(eisen) == 1 and eisen[0] == '':
            return []
        return eisen
