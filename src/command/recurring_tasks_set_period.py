"""Command for setting the period of a recurring task."""

import logging

from notion.client import NotionClient
import pendulum

import command.command as command
import repository.workspaces as workspaces
import schedules
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)
DONE_STATUS = [schema.DONE_STATUS, schema.NOT_DONE_STATUS]


class RecurringTasksSetPeriod(command.Command):
    """Command class for setting the period of a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-set-period"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the period of a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--period", dest="period", required=True, help="The period for the recurring task")
        parser.add_argument("--project", type=str, dest="project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        period = args.period.strip().lower()
        project_key = args.project

        if len(period) == 0:
            raise Exception("Must provide a non-empty project")
        if period not in [k.lower() for k in schema.INBOX_TIMELINE]:
            raise Exception(f"Invalid period value '{period}'")

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        workspace = workspace_repository.load_workspace()
        project = storage.load_project(project_key)
        LOGGER.info("Loaded the project data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        try:
            recurring_task = next(
                v for group in project["recurring_tasks"]["entries"].values()
                for v in group["tasks"] if v["ref_id"] == ref_id)
            recurring_task["period"] = period
            storage.save_project(project_key, project)
            LOGGER.info("Modified recurring task")
        except StopIteration:
            LOGGER.error(f"Recurring task with id {ref_id} does not exist")
            return

        # Apply changes in Notion

        # First, change the recurring task entry

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["recurring_tasks"]["root_page_id"])
        recurring_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project_key]["recurring_tasks"]["database_view_id"],
                collection=recurring_tasks_page.collection) \
            .build_query() \
            .execute()

        recurring_task_row = next(r for r in recurring_tasks_rows if r.ref_id == ref_id)
        recurring_task_row.period = period
        LOGGER.info("Applied Notion changes")

        # Then, change every task

        inbox_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["inbox"]["root_page_id"])
        inbox_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project_key]["inbox"]["database_view_id"],
                collection=inbox_tasks_page.collection) \
            .build_query() \
            .execute()

        # Transformations here could be "better". When moving from a higher frequency
        # to a lower one, we could end up with a case of multiple task instances
        # at old_period transforming to multiple task instances as new_period but with
        # the same name. Something like "Do Foo W14" and "Do Foo W15" transforming to
        # "Do Foo Apr" and "Do Foo Apr". We could be a bit smarter here and handle them
        # somehow - leave the latest of the bunch as a single for example. But
        # we'd also have problems by removing the tasks too. So we'll go with the
        # simple approach now and not erase anything.
        # In general, tasks that are done we won't handle!
        for inbox_task_row in inbox_tasks_rows:
            if inbox_task_row.recurring_task_id != ref_id:
                continue
            if inbox_task_row.status in DONE_STATUS:
                continue
            schedule = schedules.get_schedule(
                period, recurring_task_row.name,
                pendulum.instance(inbox_task_row.created_date.start),
                recurring_task_row.skip_rule, recurring_task_row.due_at_time,
                recurring_task_row.due_at_day, recurring_task_row.due_at_month)
            inbox_task_row.title = schedule.full_name
            setattr(inbox_task_row, schema.INBOX_TASK_ROW_PERIOD_KEY, schedule.period)
            setattr(inbox_task_row, schema.INBOX_TASK_ROW_TIMELINE_KEY, schedule.timeline)
            LOGGER.info(f"Applied Notion changes to inbox task {inbox_task_row}")
