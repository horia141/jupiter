"""Command for creating recurring tasks."""

import logging

import pendulum
import requests
from notion.client import NotionClient
# from notion.block import TodoBlock

import command.command as command
from repository.common import TaskPeriod
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks
import repository.vacations as vacations
import repository.workspaces as workspaces
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
        parser.add_argument("--project", type=str, dest="project", required=True,
                            help="Allow only tasks from this project")
        parser.add_argument("--date", required=False, default=None, help="The date on which the upsert should run at")
        parser.add_argument("--group", required=False, default=[], action="append",
                            help="The group for which the upsert should happen. Defaults to all")
        parser.add_argument("--period", required=False, default=[], action="append",
                            choices=[tp.value for tp in TaskPeriod],
                            help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        if args.date:
            right_now = pendulum.parse(args.date)
        else:
            right_now = pendulum.now()
        group_filter = frozenset(g.lower() for g in args.group) if len(args.group) > 0 else None
        period_filter = frozenset((TaskPeriod(p) for p in args.period) if len(args.period) > 0 else TaskPeriod)
        dry_run = args.dry_run

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()
        projects_repository = projects.ProjectsRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        workspace = workspace_repository.load_workspace()
        all_vacations = vacations_repository.load_all_vacations()

        project = projects_repository.load_project_by_key(project_key)
        all_recurring_tasks = recurring_tasks_repository.list_all_recurring_tasks(filter_parent_ref_id=project.ref_id)

        client = NotionClient(token_v2=workspace.token)

        project_lock = system_lock["projects"][project.key]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        # Hack for notion-py. If we don't get all the collection views for a particular page like this one
        # rather than just a single one, there's gonna be some deep code somewhere which will assume all of
        # them are present and croak! The code when you add an element to a collection, and you wanna assume
        # it's gonna be added to all view in some order!
        for key in project_lock["inbox"].keys():
            if not key.endswith("_view_id"):
                continue
            page = client.get_collection_view(project_lock["inbox"][key], collection=root_page.collection)

        all_tasks = page.build_query().execute()

        for task in all_recurring_tasks:
            RecurringTasksGen._update_notion_task(dry_run, page, right_now, group_filter, period_filter, all_vacations,
                                                  task, all_tasks)

    @staticmethod
    def _update_notion_task(dry_run, page, right_now, group_filter, period_filter, all_vacations, task, all_tasks):
        def get_possible_row(timeline):
            already_task_rows = [
                t for t in all_tasks if t.title.startswith(task.name) or t.recurring_task_id == task.ref_id]

            for already_task_row in already_task_rows:
                if timeline == already_task_row.timeline:
                    LOGGER.info(f"  - Found it again with timeline = {already_task_row.timeline}")
                    return already_task_row

            LOGGER.info("  - Need to create it")
            return page.collection.add_row()

        # def upsert_subtasks(task_row, subtasks):
        #     subtasks_to_process = {str(subtask["name"]): False for subtask in subtasks}
        #    for subtask_row in task_row.children:
        #         if subtask_row.title in subtasks_to_process:
        #             subtasks_to_process[subtask_row.title] = subtask_row.checked
        #         subtask_row.remove()
        #     for subtask in subtasks:
        #         subtask_row = task_row.children.add_new(TodoBlock)
        #         subtask_row.title = subtask["name"]
        #         subtask_row.checked = subtasks_to_process[str(subtask["name"])]

        schedule = schedules.get_schedule(
            task.period.value, task.name, right_now, task.skip_rule, task.due_at_time,
            task.due_at_day, task.due_at_month)

        if task.group != group_filter:
            LOGGER.info(f"Skipping '{task.name}' on account of group filtering")
            return

        if task.period not in period_filter:
            LOGGER.info(f"Skipping '{task.name}' on account of period filtering")
            return

        if task.suspended:
            LOGGER.info(f"Skipping '{task.name}' because it is suspended")
            return

        if not task.must_do:
            for vacation in all_vacations:
                start_date = pendulum.datetime(vacation.start_date.year, vacation.start_date.month,
                                               vacation.start_date.day, tz="UTC")
                end_date = pendulum.datetime(vacation.end_date.year, vacation.end_date.month,
                                             vacation.end_date.day, tz="UTC")
                if start_date <= schedule.first_day and schedule.end_day <= end_date:
                    LOGGER.info(
                        f"Skipping '{task.name}' on account of being fully withing vacation {start_date} to {end_date}")
                    return

        if schedule.should_skip:
            LOGGER.info(f"Skipping '{task.name}' on account of rule")
            return

        LOGGER.info(f"Creating '{task.name}'")
        try_count = 0

        if dry_run:
            return

        task_row = None
        while True:
            try:
                task_row = get_possible_row(schedule.timeline)
                task_row.name = schedule.full_name
                if task_row.status is None:
                    task_row.status = schema.RECURRING_STATUS
                task_row.recurring_task_id = task.ref_id
                task_row.created_date = right_now
                setattr(task_row, schema.INBOX_TASK_ROW_DUE_DATE_KEY, schedule.due_time)
                setattr(task_row, schema.INBOX_TASK_ROW_EISEN_KEY, task.eisen)
                setattr(
                    task_row, schema.INBOX_TASK_ROW_DIFFICULTY_KEY, task.difficulty.value if task.difficulty else None)
                setattr(task_row, schema.INBOX_TASK_ROW_FROM_SCRIPT_KEY, True)
                setattr(task_row, schema.INBOX_TASK_ROW_PERIOD_KEY, schedule.period)
                setattr(task_row, schema.INBOX_TASK_ROW_TIMELINE_KEY, schedule.timeline)

                # upsert_subtasks(task_row, subtasks)
                break
            except requests.exceptions.HTTPError as error:
                if task_row:
                    task_row.remove()
                try_count += 1
                if try_count == 3:
                    raise error
                LOGGER.info("  - Failed. Trying again")
