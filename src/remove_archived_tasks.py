import logging

from notion.client import NotionClient
import yaml

import command
import lockfile
import schedules
import schema

LOGGER = logging.getLogger(__name__)

class RemoveArchivedTasks(command.Command):

    @staticmethod
    def name():
        return "remove-archived-tasks"

    @staticmethod
    def description():
        return "Archive tasks which are done"

    def build_parser(self, parser):
        parser.add_argument("user", help="The user file")
        parser.add_argument("tasks", help="The tasks file")
        parser.add_argument("--period", required=False,  default=[], action="append", help="The period for which the upsert should happen. Defaults to all")

    def run(self, args):
        period_filter = frozenset(p.lower() for p in args.period) if len(args.period) > 0 else None

        with open(args.user, "r") as user_file:
            user = yaml.safe_load(user_file)

        with open(args.tasks, "r") as tasks_file:
            tasks = yaml.safe_load(tasks_file)

        client = NotionClient(token_v2=user["token_v2"])
        self._remove_archived_tasks(period_filter, client, tasks, args.dry_run)

    def _remove_archived_tasks(self, period_filter, client, tasks, dry_run):
        system_lock = lockfile.load_lock_file()
        project_lock = system_lock["projects"][tasks["key"]]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        page = client.get_collection_view(project_lock["inbox"]["database_view_id"], collection=root_page.collection)

        archived_tasks = page.build_query().execute()

        for archived_task in archived_tasks:
            if archived_task.status != schema.ARCHIVED_STATUS:
                continue
            if period_filter and (archived_task.script_period.lower() not in period_filter):
                LOGGER.info("Skipping '{name}' on account of period filtering".format(name=archived_task.name))
                continue
            LOGGER.info("Removing '{name}'".format(name=archived_task.name))
            if not dry_run:
                archived_task.remove()
