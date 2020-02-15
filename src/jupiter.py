import argparse
import logging

import archive_done_tasks
import create_project
import init
import remove_archived_tasks
import upsert_big_plans
import upsert_tasks

def main():

    logging.basicConfig(level=logging.INFO)

    commands = {
        init.Init.name(): init.Init(),
        create_project.CreateProject.name(): create_project.CreateProject(),
        upsert_tasks.UpsertTasks.name(): upsert_tasks.UpsertTasks(),
        upsert_big_plans.UpsertBigPlans.name(): upsert_big_plans.UpsertBigPlans(),
        archive_done_tasks.ArchiveDoneTasks.name(): archive_done_tasks.ArchiveDoneTasks(),
        remove_archived_tasks.RemoveArchivedTasks.name(): remove_archived_tasks.RemoveArchivedTasks()
    }

    parser = argparse.ArgumentParser(description="The Jupiter goal management system")
    parser.add_argument("--dry-run", required=False, dest="dry_run", action="store_true", default=False, help="Do not commit the changes")

    subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-commands help")

    for command in commands.values():
        command_parser = subparsers.add_parser(command.name(), help=command.description(), description=command.description())
        command.build_parser(command_parser)

    args = parser.parse_args()

    if not args.subparser_name in commands:
        raise Exception(f"Invalid operation {args.subparser_name}")

    commands[args.subparser_name].run(args)

if __name__ == "__main__":
    main()
