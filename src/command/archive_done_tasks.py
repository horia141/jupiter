"""Command for archiving done tasks."""

import logging

from notion.client import NotionClient

import command.command as command
import schema
import storage

DONE_STATUS = [schema.DONE_STATUS, schema.NOT_DONE_STATUS]
LOGGER = logging.getLogger(__name__)


class ArchiveDoneTasks(command.Command):
    """Command class for archiving done tasks."""

    @staticmethod
    def name():
        """The name of the command."""
        return "archive-done-tasks"

    @staticmethod
    def description():
        """The description of the command."""
        return "Archive tasks which are done"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("project", help="The key of the project")
        parser.add_argument("--period", required=False, default=[], action="append",
                            help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        period_filter = frozenset(p.lower() for p in args.period) if len(args.period) > 0 else None
        dry_run = args.dry_run

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace = storage.load_workspace()
        LOGGER.info("Found workspace file")

        _ = storage.load_project(project_key)
        LOGGER.info("Found project file")

        client = NotionClient(token_v2=workspace["token"])

        project_lock = system_lock["projects"][project_key]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        page = client.get_collection_view(project_lock["inbox"]["database_view_id"], collection=root_page.collection)

        all_done_tasks = page.build_query().execute()

        for done_task in all_done_tasks:
            task_period = getattr(done_task, schema.INBOX_TASK_ROW_PERIOD_KEY)
            if not task_period:
                task_period = ""
            if done_task.status not in DONE_STATUS:
                continue
            if period_filter and (task_period.lower() not in period_filter):
                LOGGER.info(f"Skipping '{done_task.name}' on account of period filtering")
                continue
            LOGGER.info(f"Archiving '{done_task.name}'")
            if not dry_run:
                done_task.status = schema.ARCHIVED_STATUS
