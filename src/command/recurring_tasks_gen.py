"""Command for creating recurring tasks."""

import logging

import pendulum
import requests
from notion.client import NotionClient
from notion.block import TodoBlock

import command.command as command
import schedules
import schema
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksGen(command.Command):
    """Command class for creating recurring tasks."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-gen"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create recurring tasks"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("project", help="The key of the project")
        parser.add_argument("--date", required=False, default=None, help="The date on which the upsert should run at")
        parser.add_argument("--group", required=False, default=[], action="append",
                            help="The group for which the upsert should happen. Defaults to all")
        parser.add_argument("--period", required=False, default=[], action="append",
                            help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        if args.date:
            right_now = pendulum.parse(args.date)
        else:
            right_now = pendulum.now()
        group_filter = frozenset(g.lower() for g in args.group) if len(args.group) > 0 else None
        period_filter = frozenset(p.lower() for p in args.period) if len(args.period) > 0 else schedules.PERIODS
        dry_run = args.dry_run

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace = storage.load_workspace()
        LOGGER.info("Found workspace file")

        project = storage.load_project(project_key)
        LOGGER.info("Found project file")

        client = NotionClient(token_v2=workspace["token"])

        project_lock = system_lock["projects"][project_key]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        # Hack for notion-py. If we don't get all the collection views for a particular page like this one
        # rather than just a single one, there's gonna be some deep code somewhere which will assume all of
        # them are present and croak! The code when you add an element to a collection, and you wanna assume
        # it's gonna be added to all view in some order!
        for key in project_lock["inbox"].keys():
            if not key.endswith("_view_id"):
                continue
            page = client.get_collection_view(project_lock["inbox"][key], collection=root_page.collection)

        recurring_tasks_groups = project["recurring_task"]

        all_tasks = page.build_query().execute()

        for group_name, group in recurring_tasks_groups.items():
            if group_filter is not None and group_name.lower() not in group_filter:
                LOGGER.info(f"Skipping group {group_name} on account of group filtering")
                continue
            LOGGER.info(f"Processing group {group_name}")
            RecurringTasksGen._update_notion_group(
                dry_run, page, right_now, period_filter, workspace, group, all_tasks)

    @staticmethod
    def _update_notion_group(dry_run, page, right_now, period_filter, workspace, group, all_tasks):
        group_format = group["format"]
        tasks = group["tasks"]

        for task in tasks:
            RecurringTasksGen._update_notion_task(
                dry_run, page, right_now, period_filter, group_format, workspace, task, all_tasks)

    @staticmethod
    def _update_notion_task(dry_run, page, right_now, period_filter, group_format, workspace, task, all_tasks):
        def get_possible_row(timeline):
            already_task_rows = [t for t in all_tasks if t.title.startswith(name)]

            for already_task_row in already_task_rows:
                if timeline == already_task_row.timeline:
                    LOGGER.info(f"  - Found it again with timeline = {already_task_row.timeline}")
                    return already_task_row

            LOGGER.info("  - Need to create it")
            return page.collection.add_row()

        def upsert_subtasks(task_row, subtasks):
            subtasks_to_process = {str(subtask["name"]): False for subtask in subtasks}
            for subtask_row in task_row.children:
                if subtask_row.title in subtasks_to_process:
                    subtasks_to_process[subtask_row.title] = subtask_row.checked
                subtask_row.remove()
            for subtask in subtasks:
                subtask_row = task_row.children.add_new(TodoBlock)
                subtask_row.title = subtask["name"]
                subtask_row.checked = subtasks_to_process[str(subtask["name"])]

        vacations = workspace["vacations"]["entries"]
        period = task["period"]
        name = group_format.format(name=task["name"])
        subtasks = task.get("subtasks", {})
        skip_rule = task.get("skip_rule", None)
        eisen = task.get("eisen", [])
        difficulty = task.get("difficulty", None)
        due_at_time = task.get("due_at_time", None)
        due_at_day = task.get("due_at_day", None)
        due_at_month = task.get("due_at_month", None)
        must_do = task.get("must_do", False)

        schedule = schedules.get_schedule(period, name, right_now, skip_rule, due_at_time, due_at_day, due_at_month)

        if period.lower() not in period_filter:
            LOGGER.info(f"Skipping '{name}' on account of period filtering")
            return

        if not must_do:
            for vacation in vacations:
                start_date = pendulum.datetime(vacation["start_date"].year, vacation["start_date"].month,
                                               vacation["start_date"].day, tz="UTC")
                end_date = pendulum.datetime(vacation["end_date"].year, vacation["end_date"].month,
                                             vacation["end_date"].day, tz="UTC")
                if start_date <= schedule.first_day and schedule.end_day <= end_date:
                    LOGGER.info(
                        f"Skipping '{name}' on account of being fully withing vacation {start_date} to {end_date}")
                    return

        if schedule.should_skip:
            LOGGER.info(f"Skipping '{name}' on account of rule")
            return

        LOGGER.info(f"Creating '{name}'")
        try_count = 0

        if dry_run:
            return

        while True:
            try:
                task_row = get_possible_row(schedule.timeline)
                task_row.name = schedule.full_name
                if task_row.status is None:
                    task_row.status = schema.RECURRING_STATUS
                setattr(task_row, schema.INBOX_TASK_ROW_DUE_DATE_KEY, schedule.due_time)
                setattr(task_row, schema.INBOX_TASK_ROW_EISEN_KEY, eisen)
                setattr(task_row, schema.INBOX_TASK_ROW_DIFFICULTY_KEY, difficulty)
                setattr(task_row, schema.INBOX_TASK_ROW_FROM_SCRIPT_KEY, True)
                setattr(task_row, schema.INBOX_TASK_ROW_PERIOD_KEY, schedule.period)
                setattr(task_row, schema.INBOX_TASK_ROW_TIMELINE_KEY, schedule.timeline)

                upsert_subtasks(task_row, subtasks)
                break
            except requests.exceptions.HTTPError as error:
                if task_row:
                    task_row.remove()
                try_count += 1
                if try_count == 3:
                    raise error
                LOGGER.info("  - Failed. Trying again")
