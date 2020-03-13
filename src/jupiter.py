import argparse
import logging

import commands.archive_done_tasks as archive_done_tasks
import commands.create_project as create_project
import commands.remove_archived_tasks as remove_archived_tasks
import commands.upsert_big_plans as upsert_big_plans
import commands.upsert_tasks as upsert_tasks
import commands.workspace_init as workspace_init
import commands.workspace_set_name as workspace_set_name
import commands.workspace_set_token as workspace_set_token
import commands.workspace_show as workspace_show


def main():
    logging.basicConfig(level=logging.INFO)

    commands = {
        workspace_init.WorkspaceInit.name(): workspace_init.WorkspaceInit(),
        workspace_set_name.WorkspaceSetName.name(): workspace_set_name.WorkspaceSetName(),
        workspace_set_token.WorkspaceSetToken.name(): workspace_set_token.WorkspaceSetToken(),
        workspace_show.WorkspaceShow.name(): workspace_show.WorkspaceShow(),
        create_project.CreateProject.name(): create_project.CreateProject(),
        upsert_tasks.UpsertTasks.name(): upsert_tasks.UpsertTasks(),
        upsert_big_plans.UpsertBigPlans.name(): upsert_big_plans.UpsertBigPlans(),
        archive_done_tasks.ArchiveDoneTasks.name(): archive_done_tasks.ArchiveDoneTasks(),
        remove_archived_tasks.RemoveArchivedTasks.name(): remove_archived_tasks.RemoveArchivedTasks()
    }

    parser = argparse.ArgumentParser(description="The Jupiter goal management system")
    parser.add_argument("--dry-run", required=False, dest="dry_run", action="store_true", default=False,
                        help="Do not commit the changes")

    subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-commands help")

    for command in commands.values():
        command_parser = subparsers.add_parser(command.name(), help=command.description(),
                                               description=command.description())
        command.build_parser(command_parser)

    args = parser.parse_args()

    if not args.subparser_name in commands:
        raise Exception(f"Invalid operation {args.subparser_name}")

    commands[args.subparser_name].run(args)


if __name__ == "__main__":
    main()
