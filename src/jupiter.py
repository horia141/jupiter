import argparse
import logging

import commands.archive_done_tasks as archive_done_tasks
import commands.create_project as create_project
import commands.remove_archived_tasks as remove_archived_tasks
import commands.upsert_big_plans as upsert_big_plans
import commands.upsert_tasks as upsert_tasks
import commands.vacations_add as vacations_add
import commands.vacations_remove as vacations_remove
import commands.vacations_set_name as vacations_set_name
import commands.vacations_show as vacations_show
import commands.vacations_sync as vacations_sync
import commands.workspace_init as workspace_init
import commands.workspace_set_name as workspace_set_name
import commands.workspace_set_token as workspace_set_token
import commands.workspace_show as workspace_show
import commands.workspace_sync as workspace_sync


def main():
    logging.basicConfig(level=logging.INFO)

    commands = [
        workspace_init.WorkspaceInit(),
        workspace_set_name.WorkspaceSetName(),
        workspace_set_token.WorkspaceSetToken(),
        workspace_show.WorkspaceShow(),
        workspace_sync.WorkspaceSync(),
        vacations_add.VacationsAdd(),
        vacations_remove.VacationsRemove(),
        vacations_set_name.VacationsSetName(),
        vacations_show.VacationsShow(),
        vacations_sync.VacationsSync(),
        create_project.CreateProject(),
        upsert_tasks.UpsertTasks(),
        upsert_big_plans.UpsertBigPlans(),
        archive_done_tasks.ArchiveDoneTasks(),
        remove_archived_tasks.RemoveArchivedTasks()
    ]

    parser = argparse.ArgumentParser(description="The Jupiter goal management system")
    parser.add_argument(
        "--dry-run", required=False, dest="dry_run", action="store_true", default=False,
        help="Do not commit the changes")

    subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-commands help")

    for command in commands:
        command_parser = subparsers.add_parser(
            command.name(), help=command.description(), description=command.description())
        command.build_parser(command_parser)

    args = parser.parse_args()

    for command in commands:
        if args.subparser_name != command.name():
            continue
        command.run(args)
        break


if __name__ == "__main__":
    main()
