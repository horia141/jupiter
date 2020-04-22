"""The CLI entrypoint for Jupiter."""

import argparse
import logging

import command.big_plans_archive as big_plans_archive
import command.big_plans_create as big_plans_create
import command.big_plans_set_due_date as big_plans_set_due_date
import command.big_plans_set_name as big_plans_set_name
import command.big_plans_set_status as big_plans_set_status
import command.big_plans_show as big_plans_show
import command.inbox_tasks_archive_done as inbox_tasks_archive_done
import command.inbox_tasks_archive as inbox_tasks_archive
import command.inbox_tasks_associate_big_plan as inbox_tasks_associate_big_plan
import command.inbox_tasks_create as inbox_tasks_create
import command.inbox_tasks_set_difficulty as inbox_tasks_set_difficulty
import command.inbox_tasks_set_due_date as inbox_tasks_set_due_date
import command.inbox_tasks_set_eisen as inbox_tasks_set_eisen
import command.inbox_tasks_set_name as inbox_tasks_set_name
import command.inbox_tasks_set_status as inbox_tasks_set_status
import command.inbox_tasks_show as inbox_tasks_show
import command.inbox_tasks_sync as inbox_tasks_sync
import command.project_archive as project_archive
import command.project_create as project_create
import command.project_set_name as project_set_name
import command.project_show as project_show
import command.project_sync as project_sync
import command.remove_archived_tasks as remove_archived_tasks
import command.big_plans_sync as big_plans_sync
import command.recurring_tasks_archive as recurring_tasks_archive
import command.recurring_tasks_create as recurring_tasks_create
import command.recurring_tasks_gen as recurring_tasks_gen
import command.recurring_tasks_set_deadlines as recurring_tasks_set_deadlines
import command.recurring_tasks_set_difficulty as recurring_tasks_set_difficulty
import command.recurring_tasks_set_eisen as recurring_tasks_set_eisen
import command.recurring_tasks_set_group as recurring_tasks_set_group
import command.recurring_tasks_set_must_do as recurring_tasks_set_must_do
import command.recurring_tasks_set_name as recurring_tasks_set_name
import command.recurring_tasks_set_period as recurring_tasks_set_period
import command.recurring_tasks_set_skip_rule as recurring_tasks_set_skip_rule
import command.recurring_tasks_show as recurring_tasks_show
import command.recurring_tasks_suspend as recurring_tasks_suspend
import command.recurring_tasks_sync as recurring_tasks_sync
import command.recurring_tasks_unsuspend as recurring_tasks_unsuspend
import command.vacations_create as vacations_create
import command.vacations_archive as vacations_archive
import command.vacations_set_end_date as vacations_set_end_date
import command.vacations_set_name as vacations_set_name
import command.vacations_set_start_date as vacations_set_start_date
import command.vacations_show as vacations_show
import command.vacations_sync as vacations_sync
import command.workspace_init as workspace_init
import command.workspace_set_name as workspace_set_name
import command.workspace_set_token as workspace_set_token
import command.workspace_show as workspace_show
import command.workspace_sync as workspace_sync


def main():
    """Application main function."""
    logging.basicConfig(level=logging.INFO)

    commands = [
        workspace_init.WorkspaceInit(),
        workspace_set_name.WorkspaceSetName(),
        workspace_set_token.WorkspaceSetToken(),
        workspace_show.WorkspaceShow(),
        workspace_sync.WorkspaceSync(),
        vacations_create.VacationsCreate(),
        vacations_archive.VacationsArchive(),
        vacations_set_name.VacationsSetName(),
        vacations_set_start_date.VacationsSetStartDate(),
        vacations_set_end_date.VacationsSetEndDate(),
        vacations_show.VacationsShow(),
        vacations_sync.VacationsSync(),
        project_create.ProjectCreate(),
        project_archive.ProjectArchive(),
        project_set_name.ProjectSetName(),
        project_show.ProjectShow(),
        project_sync.ProjectSync(),
        inbox_tasks_create.InboxTasksCreate(),
        inbox_tasks_archive.InboxTasksArchive(),
        inbox_tasks_associate_big_plan.InboxTasksAssociateBigPlan(),
        inbox_tasks_set_name.InboxTasksSetName(),
        inbox_tasks_set_status.InboxTasksSetStatus(),
        inbox_tasks_set_eisen.InboxTasksSetEisen(),
        inbox_tasks_set_difficulty.InboxTasksSetDifficulty(),
        inbox_tasks_set_due_date.InboxTasksSetDueDate(),
        inbox_tasks_archive_done.InboxTasksArchiveDone(),
        inbox_tasks_show.InboxTasksShow(),
        inbox_tasks_sync.InboxTasksSync(),
        recurring_tasks_create.RecurringTasksCreate(),
        recurring_tasks_archive.RecurringTasksArchive(),
        recurring_tasks_gen.RecurringTasksGen(),
        recurring_tasks_set_name.RecurringTasksSetName(),
        recurring_tasks_set_period.RecurringTasksSetPeriod(),
        recurring_tasks_set_group.RecurringTasksSetGroup(),
        recurring_tasks_set_eisen.RecurringTasksSetEisen(),
        recurring_tasks_set_difficulty.RecurringTasksSetDifficulty(),
        recurring_tasks_set_deadlines.RecurringTasksSetDeadlines(),
        recurring_tasks_set_skip_rule.RecurringTasksSetSkipRule(),
        recurring_tasks_set_must_do.RecurringTasksSetMustDo(),
        recurring_tasks_suspend.RecurringTasksSuspend(),
        recurring_tasks_unsuspend.RecurringTasksUnsuspend(),
        recurring_tasks_show.RecurringTasksShow(),
        recurring_tasks_sync.RecurringTasksSync(),
        big_plans_create.BigPlansCreate(),
        big_plans_archive.BigPlansArchive(),
        big_plans_set_due_date.BigPlansSetDueDate(),
        big_plans_set_name.BigPlansSetName(),
        big_plans_set_status.BigPlansSetStatus(),
        big_plans_sync.BigPlansSync(),
        big_plans_show.BigPlansShow(),
        remove_archived_tasks.RemoveArchivedTasks()
    ]

    parser = argparse.ArgumentParser(description="The Jupiter goal management system")
    parser.add_argument(
        "--dry-run", required=False, dest="dry_run", action="store_true", default=False,
        help="Do not commit the changes")

    subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-command help")

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
