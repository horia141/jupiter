"""Command for creating recurring tasks."""

import logging
from typing import Optional

import pendulum
import requests
from notion.client import NotionClient
# from notion.block import TodoBlock

import command.command as command
import models.basic
from models.basic import BasicValidator
import repository.inbox_tasks as inbox_tasks
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
        parser.add_argument("--project", dest="project_key", required=True,
                            help="Allow only tasks from this project")
        parser.add_argument("--date", help="The date on which the upsert should run at")
        parser.add_argument("--group", default=[], action="append",
                            help="The groups for which the upsert should happen. Defaults to all")
        parser.add_argument("--period", default=[], action="append",
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        project_key = basic_validator.project_key_validate_and_clean(args.project_key)
        right_now = basic_validator.datetime_validate_and_clean(args.date) if args.date else pendulum.now()
        group_filter = frozenset(basic_validator.entity_name_validate_and_clean(g) for g in args.group) \
            if len(args.group) > 0 else None
        period_filter = frozenset(basic_validator.recurring_task_period_validate_and_clean(p) for p in args.period) \
            if len(args.period) > 0 else None
        dry_run = args.dry_run

        # Load the local data
        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()
        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        workspace = workspace_repository.load_workspace()
        all_vacations = vacations_repository.load_all_vacations()

        project = projects_repository.load_project_by_key(project_key)
        all_recurring_tasks = recurring_tasks_repository.list_all_recurring_tasks(
            filter_project_ref_id=[project.ref_id])

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

        all_tasks = inbox_tasks_repository.list_all_inbox_tasks(
            filter_project_ref_id=[project.ref_id])
        inbox_tasks_rows = client \
            .get_collection_view(
                project_lock["inbox"]["database_view_id"],
                collection=root_page.collection) \
            .build_query() \
            .execute()
        for task in all_recurring_tasks:
            RecurringTasksGen._update_notion_task(
                project, dry_run, page, right_now, group_filter, period_filter, all_vacations,
                task, all_tasks, inbox_tasks_rows, inbox_tasks_repository)

    @staticmethod
    def _update_notion_task(
            project, dry_run, page, right_now, group_filter, period_filter, all_vacations, task, all_tasks,
            inbox_tasks_rows, inbox_tasks_repository):
        def get_possible_row(timeline) -> Optional[inbox_tasks.InboxTask]:
            already_task_rows = [
                t for t in all_tasks if t.name.startswith(task.name) or t.recurring_task_ref_id == task.ref_id]

            for already_task_row in already_task_rows:
                if timeline == already_task_row.recurring_task_timeline:
                    LOGGER.info(f"  - Found it again with timeline = {already_task_row.recurring_task_timeline}")
                    return already_task_row

            LOGGER.info("  - Need to create it")
            return None

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

        if group_filter is not None and task.group not in group_filter:
            LOGGER.info(f"Skipping '{task.name}' on account of group filtering")
            return

        if period_filter is not None and task.period not in period_filter:
            LOGGER.info(f"Skipping '{task.name}' on account of period filtering")
            return

        if task.suspended:
            LOGGER.info(f"Skipping '{task.name}' because it is suspended")
            return

        if not task.must_do:
            for vacation in all_vacations:
                if vacation.is_in_vacation(schedule.first_day, schedule.end_day):
                    LOGGER.info(
                        f"Skipping '{task.name}' on account of being fully withing vacation {vacation}")
                    return

        if schedule.should_skip:
            LOGGER.info(f"Skipping '{task.name}' on account of rule")
            return

        LOGGER.info(f"Creating '{task.name}'")
        try_count = 0

        if dry_run:
            return

        found_task = None
        while True:
            try:
                found_task = get_possible_row(schedule.timeline)
                found_task_row = None

                if found_task:
                    found_task.name = schedule.full_name
                    found_task.due_date = schedule.due_time
                    found_task.eisen = task.eisen
                    found_task.difficulty = task.difficulty
                    found_task.recurring_task_timeline = schedule.timeline

                    found_task_row = next((r for r in inbox_tasks_rows if r.ref_id == found_task.ref_id), None)
                else:
                    found_task = inbox_tasks_repository.create_inbox_task(
                        project_ref_id=project.ref_id,
                        big_plan_ref_id=None,
                        recurring_task_ref_id=task.ref_id,
                        created_date=right_now,
                        name=schedule.full_name,
                        archived=False,
                        status=models.basic.InboxTaskStatus.RECURRING,
                        eisen=task.eisen,
                        difficulty=task.difficulty,
                        due_date=schedule.due_time,
                        recurring_task_timeline=schedule.timeline)

                if not found_task_row:
                    found_task_row = page.collection.add_row()

                found_task_row.name = schedule.full_name
                if found_task_row.status is None:
                    found_task_row.status = schema.RECURRING_STATUS
                found_task_row.recurring_task_id = task.ref_id
                found_task_row.created_date = found_task.created_date
                setattr(found_task_row, schema.INBOX_TASK_ROW_DUE_DATE_KEY, schedule.due_time)
                setattr(found_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, [e.value for e in task.eisen])
                setattr(
                    found_task_row, schema.INBOX_TASK_ROW_DIFFICULTY_KEY,
                    task.difficulty.value if task.difficulty else None)
                setattr(found_task_row, schema.INBOX_TASK_ROW_FROM_SCRIPT_KEY, True)
                setattr(found_task_row, schema.INBOX_TASK_ROW_PERIOD_KEY, schedule.period)
                setattr(found_task_row, schema.INBOX_TASK_ROW_TIMELINE_KEY, schedule.timeline)

                # upsert_subtasks(task_row, subtasks)
                break
            except requests.exceptions.HTTPError as error:
                if found_task_row:
                    found_task_row.remove()
                try_count += 1
                if try_count == 3:
                    raise error
                LOGGER.info("  - Failed. Trying again")
