"""Command for archiving done tasks."""

import logging

from notion.client import NotionClient
import yaml

import command.command as command
import lockfile
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
        parser.add_argument("tasks", help="The tasks file")
        parser.add_argument("--period", required=False, default=[], action="append",
                            help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        period_filter = frozenset(p.lower() for p in args.period) if len(args.period) > 0 else None

        workspace = storage.load_workspace()

        with open(args.tasks, "r") as tasks_file:
            tasks = yaml.safe_load(tasks_file)

        client = NotionClient(token_v2=workspace["token"])

        self._archive_done_tasks(period_filter, client, tasks, args.dry_run)

    @staticmethod
    def _archive_done_tasks(period_filter, client, tasks, dry_run):

        system_lock = lockfile.load_lock_file()
        project_lock = system_lock["projects"][tasks["key"]]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        page = client.get_collection_view(project_lock["inbox"]["database_view_id"], collection=root_page.collection)

        all_done_tasks = page.build_query().execute()

        for done_task in all_done_tasks:
            if done_task.status not in DONE_STATUS:
                continue
            if period_filter and (done_task.script_period.lower() not in period_filter):
                LOGGER.info(f"Skipping '{done_task.name}' on account of period filtering")
                continue
            LOGGER.info(f"Archiving '{done_task.name}'")
            if not dry_run:
                done_task.status = schema.ARCHIVED_STATUS
