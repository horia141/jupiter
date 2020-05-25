"""The CLI entry-point for Jupiter."""

import argparse
import logging

from command.big_plans_archive import BigPlansArchive
from command.big_plans_create import BigPlansCreate
from command.big_plans_set_due_date import BigPlansSetDueDate
from command.big_plans_set_name import BigPlansSetName
from command.big_plans_set_status import BigPlansSetStatus
from command.big_plans_show import BigPlansShow
from command.big_plans_sync import BigPlansSync
from command.inbox_tasks_archive import InboxTasksArchive
from command.inbox_tasks_archive_done import InboxTasksArchiveDone
from command.inbox_tasks_associate_big_plan import InboxTasksAssociateBigPlan
from command.inbox_tasks_create import InboxTasksCreate
from command.inbox_tasks_set_difficulty import InboxTasksSetDifficulty
from command.inbox_tasks_set_due_date import InboxTasksSetDueDate
from command.inbox_tasks_set_eisen import InboxTasksSetEisen
from command.inbox_tasks_set_name import InboxTasksSetName
from command.inbox_tasks_set_status import InboxTasksSetStatus
from command.inbox_tasks_show import InboxTasksShow
from command.inbox_tasks_sync import InboxTasksSync
from command.project_archive import ProjectArchive
from command.project_create import ProjectCreate
from command.project_set_name import ProjectSetName
from command.project_show import ProjectShow
from command.project_sync import ProjectSync
from command.recurring_tasks_archive import RecurringTasksArchive
from command.recurring_tasks_create import RecurringTasksCreate
from command.recurring_tasks_gen import RecurringTasksGen
from command.recurring_tasks_set_deadlines import RecurringTasksSetDeadlines
from command.recurring_tasks_set_difficulty import RecurringTasksSetDifficulty
from command.recurring_tasks_set_eisen import RecurringTasksSetEisen
from command.recurring_tasks_set_group import RecurringTasksSetGroup
from command.recurring_tasks_set_must_do import RecurringTasksSetMustDo
from command.recurring_tasks_set_name import RecurringTasksSetName
from command.recurring_tasks_set_period import RecurringTasksSetPeriod
from command.recurring_tasks_set_skip_rule import RecurringTasksSetSkipRule
from command.recurring_tasks_show import RecurringTasksShow
from command.recurring_tasks_suspend import RecurringTasksSuspend
from command.recurring_tasks_sync import RecurringTasksSync
from command.recurring_tasks_unsuspend import RecurringTasksUnsuspend
from command.vacations_archive import VacationsArchive
from command.vacations_create import VacationsCreate
from command.vacations_set_end_date import VacationsSetEndDate
from command.vacations_set_name import VacationsSetName
from command.vacations_set_start_date import VacationsSetStartDate
from command.vacations_show import VacationsShow
from command.vacations_sync import VacationsSync
from command.workspace_init import WorkspaceInit
from command.workspace_set_name import WorkspaceSetName
from command.workspace_set_token import WorkspaceSetToken
from command.workspace_show import WorkspaceShow
from command.workspace_sync import WorkspaceSync
from controllers.big_plans import BigPlansController
from controllers.inbox_tasks import InboxTasksController
from controllers.projects import ProjectsController
from controllers.recurring_tasks import RecurringTasksController
from controllers.vacations import VacationsController
from controllers.workspaces import WorkspacesController
from models.basic import BasicValidator
from remote.notion.big_plans import BigPlansCollection
from remote.notion.connection import MissingNotionConnectionError, OldTokenForNotionConnectionError, NotionConnection
from remote.notion.inbox_tasks import InboxTasksCollection
from remote.notion.projects import ProjectsCollection
from remote.notion.recurring_tasks import RecurringTasksCollection
from remote.notion.vacations import VacationsCollection
from remote.notion.workspaces import WorkspaceSingleton, MissingWorkspaceScreenError
from repository.big_plans import BigPlansRepository
from repository.inbox_tasks import InboxTasksRepository
from repository.projects import ProjectsRepository
from repository.recurring_tasks import RecurringTasksRepository
from repository.vacations import VacationsRepository
from repository.workspace import WorkspaceRepository, MissingWorkspaceRepositoryError
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService


def main() -> None:
    """Application main function."""
    basic_validator = BasicValidator()

    notion_connection = NotionConnection()

    workspaces_repository = WorkspaceRepository()
    workspaces_singleton = WorkspaceSingleton(notion_connection)

    with VacationsRepository() as vacations_repository,\
            ProjectsRepository() as projects_repository,\
            InboxTasksRepository() as inbox_tasks_repository,\
            RecurringTasksRepository() as recurring_tasks_repository,\
            BigPlansRepository() as big_plans_repository, \
            VacationsCollection(notion_connection) as vacations_collection, \
            ProjectsCollection(notion_connection) as projects_collection, \
            InboxTasksCollection(notion_connection) as inbox_tasks_collection, \
            RecurringTasksCollection(notion_connection) as recurring_tasks_collection, \
            BigPlansCollection(notion_connection) as big_plans_collection:
        workspaces_service = WorkspacesService(
            basic_validator, workspaces_repository, workspaces_singleton)
        vacations_service = VacationsService(basic_validator, vacations_repository, vacations_collection)
        projects_service = ProjectsService(
            basic_validator, projects_repository, projects_collection)
        inbox_tasks_service = InboxTasksService(
            basic_validator, inbox_tasks_repository, inbox_tasks_collection)
        recurring_tasks_service = RecurringTasksService(
            basic_validator, recurring_tasks_repository, recurring_tasks_collection)
        big_plans_service = BigPlansService(basic_validator, big_plans_repository, big_plans_collection)

        workspaces_controller = WorkspacesController(notion_connection, workspaces_service, vacations_service)
        vacations_controller = VacationsController(vacations_service)
        projects_controller = ProjectsController(
            workspaces_service, projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service)
        inbox_tasks_controller = InboxTasksController(
            projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service)
        recurring_tasks_controller = RecurringTasksController(
            projects_service, vacations_service, inbox_tasks_service, recurring_tasks_service)
        big_plans_controller = BigPlansController(projects_service, inbox_tasks_service, big_plans_service)

        commands = [
            WorkspaceInit(basic_validator, workspaces_controller),
            WorkspaceSetName(basic_validator, workspaces_controller),
            WorkspaceSetToken(basic_validator, workspaces_controller),
            WorkspaceShow(workspaces_controller),
            WorkspaceSync(basic_validator, workspaces_controller),
            VacationsCreate(basic_validator, vacations_controller),
            VacationsArchive(basic_validator, vacations_controller),
            VacationsSetName(basic_validator, vacations_controller),
            VacationsSetStartDate(basic_validator, vacations_controller),
            VacationsSetEndDate(basic_validator, vacations_controller),
            VacationsShow(vacations_controller),
            VacationsSync(basic_validator, vacations_controller),
            ProjectCreate(basic_validator, projects_controller),
            ProjectArchive(basic_validator, projects_controller),
            ProjectSetName(basic_validator, projects_controller),
            ProjectShow(basic_validator, projects_controller),
            ProjectSync(basic_validator, projects_controller),
            InboxTasksCreate(basic_validator, inbox_tasks_controller),
            InboxTasksArchive(basic_validator, inbox_tasks_controller),
            InboxTasksAssociateBigPlan(basic_validator, inbox_tasks_controller),
            InboxTasksSetName(basic_validator, inbox_tasks_controller),
            InboxTasksSetStatus(basic_validator, inbox_tasks_controller),
            InboxTasksSetEisen(basic_validator, inbox_tasks_controller),
            InboxTasksSetDifficulty(basic_validator, inbox_tasks_controller),
            InboxTasksSetDueDate(basic_validator, inbox_tasks_controller),
            InboxTasksArchiveDone(basic_validator, inbox_tasks_controller),
            InboxTasksShow(basic_validator, inbox_tasks_controller),
            InboxTasksSync(basic_validator, inbox_tasks_controller),
            RecurringTasksCreate(basic_validator, recurring_tasks_controller),
            RecurringTasksArchive(basic_validator, recurring_tasks_controller),
            RecurringTasksGen(basic_validator, recurring_tasks_controller),
            RecurringTasksSetName(basic_validator, recurring_tasks_controller),
            RecurringTasksSetPeriod(basic_validator, recurring_tasks_controller),
            RecurringTasksSetGroup(basic_validator, recurring_tasks_controller),
            RecurringTasksSetEisen(basic_validator, recurring_tasks_controller),
            RecurringTasksSetDifficulty(basic_validator, recurring_tasks_controller),
            RecurringTasksSetDeadlines(basic_validator, recurring_tasks_controller),
            RecurringTasksSetSkipRule(basic_validator, recurring_tasks_controller),
            RecurringTasksSetMustDo(basic_validator, recurring_tasks_controller),
            RecurringTasksSuspend(basic_validator, recurring_tasks_controller),
            RecurringTasksUnsuspend(basic_validator, recurring_tasks_controller),
            RecurringTasksShow(basic_validator, recurring_tasks_controller),
            RecurringTasksSync(basic_validator, recurring_tasks_controller),
            BigPlansCreate(basic_validator, big_plans_controller),
            BigPlansArchive(basic_validator, big_plans_controller),
            BigPlansSetDueDate(basic_validator, big_plans_controller),
            BigPlansSetName(basic_validator, big_plans_controller),
            BigPlansSetStatus(basic_validator, big_plans_controller),
            BigPlansSync(basic_validator, big_plans_controller),
            BigPlansShow(basic_validator, big_plans_controller)
        ]

        parser = argparse.ArgumentParser(description="The Jupiter goal management system")
        parser.add_argument(
            "--min-log-level", dest="min_log_level", default="info",
            choices=["debug", "info", "warning", "error", "critical"],
            help="The logging level to use")

        subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-command help")

        for command in commands:
            command_parser = subparsers.add_parser(
                command.name(), help=command.description(), description=command.description())
            command.build_parser(command_parser)

        args = parser.parse_args()
        logging.basicConfig(level=_map_log_level_to_log_class(args.min_log_level))

        try:
            for command in commands:
                if args.subparser_name != command.name():
                    continue
                command.run(args)
                break
        except (MissingWorkspaceRepositoryError, MissingNotionConnectionError, MissingWorkspaceScreenError):
            print("The Notion connection isn't setup, please run 'ws-init' to create a workspace!")
        except OldTokenForNotionConnectionError:
            print("The Notion connection's token has expired, please refresh it with 'ws-set-token'")


def _map_log_level_to_log_class(log_level: str) -> int:
    if log_level == "debug":
        return logging.DEBUG
    elif log_level == "info":
        return logging.INFO
    elif log_level == "warning":
        return logging.WARNING
    elif log_level == "error":
        return logging.ERROR
    elif log_level == "critical":
        return logging.CRITICAL
    else:
        raise Exception(f"Invalid log level '{log_level}'")


if __name__ == "__main__":
    main()
