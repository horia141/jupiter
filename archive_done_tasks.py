import logging

from notion.client import NotionClient
import yaml

import command
import lockfile
import schedules
import schema

DONE_STATUS = [ schema.DONE_STATUS, schema.NOT_DONE_STATUS ]
LOGGER = logging.getLogger(__name__)

class ArchiveDoneTasks(command.Command):

    @staticmethod
    def name():
        return "archive-done-tasks"

    @staticmethod
    def description():
        return "Archive tasks which are done"

    def build_parser(self, parser):
        parser.add_argument("tasks", help="The tasks file")
        parser.add_argument("--period", required=False,  default=[], action="append", help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):

        client = NotionClient(token_v2=user["token_v2"])
        period_filter = frozenset(p.lower() for p in args.period) if len(args.period) > 0 else None

        with open(args.tasks, "r") as tasks_file:
            tasks = yaml.load(tasks_file)

        self._archive_done_tasks(period_filter, client, tasks, args.dry_run)

    def _archive_done_tasks(self, period_filter, client, tasks, dry_run):

        system_lock = lockfile.get_lock_file()
        project_lock = system_lock["projects"][tasks["key"]]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        page = client.get_collection_view(project_lock["inbox"]["database_view_id"], collection=root_page.collection)

        all_done_tasks = page.build_query().execute()

        for done_task in all_done_tasks:
            if done_task.status not in DONE_STATUS:
                continue
            if period_filter and (done_task.script_period.lower() not in period_filter):
                LOGGER.info("Skipping '{name}' on account of period filtering".format(name=done_task.name))
                continue
            LOGGER.info("Archiving '{name}'".format(name=done_task.name))
            if not dry_run:
                done_task.status = schema.ARCHIVED_STATUS
