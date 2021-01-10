"""The CLI entry-point for Jupiter."""

import argparse
import logging
import os
from pathlib import Path
from typing import cast

import coloredlogs
import dotenv
import pendulum

from command.big_plans_archive import BigPlansArchive
from command.big_plans_create import BigPlansCreate
from command.big_plans_hard_remove import BigPlansHardRemove
from command.big_plans_set_due_date import BigPlansSetDueDate
from command.big_plans_set_name import BigPlansSetName
from command.big_plans_set_status import BigPlansSetStatus
from command.big_plans_show import BigPlansShow
from command.inbox_tasks_archive import InboxTasksArchive
from command.garbage_collect import GarbageCollect
from command.inbox_tasks_associate_big_plan import InboxTasksAssociateBigPlan
from command.inbox_tasks_create import InboxTasksCreate
from command.inbox_tasks_hard_remove import InboxTasksHardRemove
from command.inbox_tasks_set_actionable_date import InboxTasksSetActiveDate
from command.inbox_tasks_set_difficulty import InboxTasksSetDifficulty
from command.inbox_tasks_set_due_date import InboxTasksSetDueDate
from command.inbox_tasks_set_eisen import InboxTasksSetEisen
from command.inbox_tasks_set_name import InboxTasksSetName
from command.inbox_tasks_set_status import InboxTasksSetStatus
from command.inbox_tasks_show import InboxTasksShow
from command.projects_archive import ProjectArchive
from command.projects_create import ProjectCreate
from command.projects_set_name import ProjectSetName
from command.projects_show import ProjectShow
from command.recurring_tasks_archive import RecurringTasksArchive
from command.recurring_tasks_create import RecurringTasksCreate
from command.generate_inbox_tasks import GenerateInboxTasks
from command.recurring_tasks_hard_remove import RecurringTasksHardRemove
from command.recurring_tasks_set_actionable_config import RecurringTasksSetActionableConfig
from command.recurring_tasks_set_active_interval import RecurringTasksSetActiveInterval
from command.recurring_tasks_set_deadlines import RecurringTasksSetDeadlines
from command.recurring_tasks_set_difficulty import RecurringTasksSetDifficulty
from command.recurring_tasks_set_eisen import RecurringTasksSetEisen
from command.recurring_tasks_set_must_do import RecurringTasksSetMustDo
from command.recurring_tasks_set_name import RecurringTasksSetName
from command.recurring_tasks_set_period import RecurringTasksSetPeriod
from command.recurring_tasks_set_skip_rule import RecurringTasksSetSkipRule
from command.recurring_tasks_set_type import RecurringTasksSetType
from command.recurring_tasks_show import RecurringTasksShow
from command.recurring_tasks_suspend import RecurringTasksSuspend
from command.recurring_tasks_unsuspend import RecurringTasksUnsuspend
from command.report_progress import ReportProgress
from command.smart_lists_archive import SmartListsArchive
from command.smart_lists_hard_remove import SmartListsHardRemove
from command.smart_lists_item_archive import SmartListsItemArchive
from command.smart_lists_item_create import SmartListsItemCreate
from command.smart_lists_create import SmartListsCreate
from command.smart_lists_item_hard_remove import SmartListsItemHardRemove
from command.smart_lists_item_mark_done import SmartListsItemMarkDone
from command.smart_lists_item_mark_undone import SmartListsItemMarkUndone
from command.smart_lists_item_set_name import SmartListsItemSetName
from command.smart_lists_item_set_tags import SmartListsItemSetTags
from command.smart_lists_item_set_url import SmartListsItemSetUrl
from command.smart_lists_item_show import SmartListsItemShow
from command.smart_lists_set_name import SmartListsSetName
from command.smart_lists_show import SmartListsShow
from command.smart_lists_tag_archive import SmartListsTagArchive
from command.smart_lists_tag_create import SmartListsTagCreate
from command.smart_lists_tag_hard_remove import SmartListsTagHardRemove
from command.smart_lists_tag_set_name import SmartListsTagSetName
from command.smart_lists_tag_show import SmartListsTagShow
from command.sync_local_and_notion import SyncLocalAndNotion
from command.vacations_archive import VacationsArchive
from command.vacations_create import VacationsCreate
from command.vacations_hard_remove import VacationsHardRemove
from command.vacations_set_end_date import VacationsSetEndDate
from command.vacations_set_name import VacationsSetName
from command.vacations_set_start_date import VacationsSetStartDate
from command.vacations_show import VacationsShow
from command.workspace_init import WorkspaceInit
from command.workspace_set_name import WorkspaceSetName
from command.workspace_set_timezone import WorkspaceSetTimezone
from command.workspace_set_token import WorkspaceSetToken
from command.workspace_show import WorkspaceShow
from controllers.big_plans import BigPlansController
from controllers.garbage_collect_notion import GarbageCollectNotionController
from controllers.inbox_tasks import InboxTasksController
from controllers.projects import ProjectsController
from controllers.recurring_tasks import RecurringTasksController
from controllers.generate_inbox_tasks import GenerateInboxTasksController
from controllers.report_progress import ReportProgressController
from controllers.smart_lists import SmartListsController
from controllers.sync_local_and_notion import SyncLocalAndNotionController
from controllers.vacations import VacationsController
from controllers.workspaces import WorkspacesController
from models.basic import BasicValidator
from remote.notion.big_plans import BigPlansCollection
from remote.notion.common import CollectionEntityNotFound, CollectionEntityAlreadyExists
from remote.notion.infra.collections_manager import CollectionsManager
from remote.notion.infra.connection import \
    MissingNotionConnectionError, OldTokenForNotionConnectionError, NotionConnection
from remote.notion.inbox_tasks import InboxTasksCollection
from remote.notion.infra.pages_manager import PagesManager
from remote.notion.projects_manager import NotionProjectsManager
from remote.notion.smart_lists_manager import NotionSmartListsManager
from remote.notion.recurring_tasks import RecurringTasksCollection
from remote.notion.vacations_manager import NotionVacationsManager
from remote.notion.workspaces import WorkspaceSingleton, MissingWorkspaceScreenError
from repository.big_plans import BigPlansRepository
from repository.inbox_tasks import InboxTasksRepository
from repository.smart_lists import SmartListsRepository, SmartListItemsRepository, SmartListTagsRepository
from repository.projects import ProjectsRepository
from repository.recurring_tasks import RecurringTasksRepository
from repository.vacations import VacationsRepository
from repository.workspace import WorkspaceRepository, MissingWorkspaceRepositoryError
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.smart_lists import SmartListsService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    notion_connection = NotionConnection()

    workspaces_repository = WorkspaceRepository(time_provider)
    workspaces_singleton = WorkspaceSingleton(notion_connection)

    global_properties = _build_global_properties(workspaces_repository)
    basic_validator = BasicValidator(global_properties)

    with VacationsRepository(time_provider) as vacations_repository, \
            ProjectsRepository(time_provider) as projects_repository, \
            InboxTasksRepository(time_provider) as inbox_tasks_repository, \
            RecurringTasksRepository(time_provider) as recurring_tasks_repository, \
            BigPlansRepository(time_provider) as big_plans_repository, \
            SmartListsRepository(time_provider) as smart_lists_repository, \
            SmartListTagsRepository(time_provider) as smart_list_tags_repository, \
            SmartListItemsRepository(time_provider) as smart_list_items_repository, \
            InboxTasksCollection(time_provider, basic_validator, notion_connection) as inbox_tasks_collection, \
            RecurringTasksCollection(time_provider, basic_validator, notion_connection) as recurring_tasks_collection, \
            BigPlansCollection(time_provider, basic_validator, notion_connection) as big_plans_collection, \
            PagesManager(time_provider, notion_connection) as pages_manager, \
            CollectionsManager(time_provider, notion_connection) as collections_manager:
        notion_vacations_manager = NotionVacationsManager(
            time_provider, basic_validator, collections_manager)
        notion_projects_manager = NotionProjectsManager(pages_manager)
        notion_smart_lists_manager = NotionSmartListsManager(
            time_provider, basic_validator, pages_manager, collections_manager)

        workspaces_service = WorkspacesService(
            basic_validator, workspaces_repository, workspaces_singleton)
        vacations_service = VacationsService(
            basic_validator, vacations_repository, notion_vacations_manager)
        projects_service = ProjectsService(
            basic_validator, projects_repository, notion_projects_manager)
        inbox_tasks_service = InboxTasksService(
            basic_validator, inbox_tasks_repository, inbox_tasks_collection)
        recurring_tasks_service = RecurringTasksService(
            basic_validator, time_provider, recurring_tasks_repository, recurring_tasks_collection)
        big_plans_service = BigPlansService(basic_validator, big_plans_repository, big_plans_collection)
        smart_lists_service = SmartListsService(
            basic_validator, smart_lists_repository, smart_list_tags_repository, smart_list_items_repository,
            notion_smart_lists_manager)

        workspaces_controller = WorkspacesController(
            notion_connection, workspaces_service, vacations_service, projects_service, smart_lists_service)
        vacations_controller = VacationsController(vacations_service)
        projects_controller = ProjectsController(
            projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service)
        inbox_tasks_controller = InboxTasksController(
            projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service)
        recurring_tasks_controller = RecurringTasksController(
            global_properties, projects_service, inbox_tasks_service, recurring_tasks_service)
        big_plans_controller = BigPlansController(projects_service, inbox_tasks_service, big_plans_service)
        smart_lists_controller = SmartListsController(smart_lists_service)
        sync_local_and_notion_controller = SyncLocalAndNotionController(
            time_provider, global_properties, workspaces_service, vacations_service, projects_service,
            inbox_tasks_service, recurring_tasks_service, big_plans_service, smart_lists_service)
        generate_inbox_tasks_controller = GenerateInboxTasksController(
            global_properties, projects_service, vacations_service, inbox_tasks_service, recurring_tasks_service)
        report_progress_controller = ReportProgressController(
            global_properties, projects_service, inbox_tasks_service, big_plans_service, recurring_tasks_service)
        garbage_collect_controller = GarbageCollectNotionController(
            vacations_service, projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service,
            smart_lists_service)

        commands = [
            # CRUD Commands
            WorkspaceInit(basic_validator, workspaces_controller),
            WorkspaceSetName(basic_validator, workspaces_controller),
            WorkspaceSetTimezone(basic_validator, workspaces_controller),
            WorkspaceSetToken(basic_validator, workspaces_controller),
            WorkspaceShow(workspaces_controller),
            VacationsCreate(basic_validator, vacations_controller),
            VacationsArchive(basic_validator, vacations_controller),
            VacationsSetName(basic_validator, vacations_controller),
            VacationsSetStartDate(basic_validator, vacations_controller),
            VacationsSetEndDate(basic_validator, vacations_controller),
            VacationsHardRemove(basic_validator, vacations_controller),
            VacationsShow(basic_validator, vacations_controller),
            ProjectCreate(basic_validator, projects_controller),
            ProjectArchive(basic_validator, projects_controller),
            ProjectSetName(basic_validator, projects_controller),
            ProjectShow(basic_validator, projects_controller),
            InboxTasksCreate(basic_validator, inbox_tasks_controller),
            InboxTasksArchive(basic_validator, inbox_tasks_controller),
            InboxTasksAssociateBigPlan(basic_validator, inbox_tasks_controller),
            InboxTasksSetName(basic_validator, inbox_tasks_controller),
            InboxTasksSetStatus(basic_validator, inbox_tasks_controller),
            InboxTasksSetEisen(basic_validator, inbox_tasks_controller),
            InboxTasksSetDifficulty(basic_validator, inbox_tasks_controller),
            InboxTasksSetActiveDate(basic_validator, inbox_tasks_controller),
            InboxTasksSetDueDate(basic_validator, inbox_tasks_controller),
            InboxTasksHardRemove(basic_validator, inbox_tasks_controller),
            InboxTasksShow(basic_validator, inbox_tasks_controller),
            RecurringTasksCreate(basic_validator, recurring_tasks_controller),
            RecurringTasksArchive(basic_validator, recurring_tasks_controller),
            RecurringTasksSetName(basic_validator, recurring_tasks_controller),
            RecurringTasksSetPeriod(basic_validator, recurring_tasks_controller),
            RecurringTasksSetType(basic_validator, recurring_tasks_controller),
            RecurringTasksSetEisen(basic_validator, recurring_tasks_controller),
            RecurringTasksSetDifficulty(basic_validator, recurring_tasks_controller),
            RecurringTasksSetActionableConfig(basic_validator, recurring_tasks_controller),
            RecurringTasksSetDeadlines(basic_validator, recurring_tasks_controller),
            RecurringTasksSetSkipRule(basic_validator, recurring_tasks_controller),
            RecurringTasksSetMustDo(basic_validator, recurring_tasks_controller),
            RecurringTasksSetActiveInterval(basic_validator, recurring_tasks_controller),
            RecurringTasksSuspend(basic_validator, recurring_tasks_controller),
            RecurringTasksUnsuspend(basic_validator, recurring_tasks_controller),
            RecurringTasksHardRemove(basic_validator, recurring_tasks_controller),
            RecurringTasksShow(basic_validator, recurring_tasks_controller),
            BigPlansCreate(basic_validator, big_plans_controller),
            BigPlansArchive(basic_validator, big_plans_controller),
            BigPlansSetDueDate(basic_validator, big_plans_controller),
            BigPlansSetName(basic_validator, big_plans_controller),
            BigPlansSetStatus(basic_validator, big_plans_controller),
            BigPlansHardRemove(basic_validator, big_plans_controller),
            BigPlansShow(basic_validator, big_plans_controller),
            SmartListsCreate(basic_validator, smart_lists_controller),
            SmartListsArchive(basic_validator, smart_lists_controller),
            SmartListsSetName(basic_validator, smart_lists_controller),
            SmartListsShow(basic_validator, smart_lists_controller),
            SmartListsHardRemove(basic_validator, smart_lists_controller),
            SmartListsTagCreate(basic_validator, smart_lists_controller),
            SmartListsTagArchive(basic_validator, smart_lists_controller),
            SmartListsTagSetName(basic_validator, smart_lists_controller),
            SmartListsTagShow(basic_validator, smart_lists_controller),
            SmartListsTagHardRemove(basic_validator, smart_lists_controller),
            SmartListsItemCreate(basic_validator, smart_lists_controller),
            SmartListsItemArchive(basic_validator, smart_lists_controller),
            SmartListsItemSetName(basic_validator, smart_lists_controller),
            SmartListsItemMarkDone(basic_validator, smart_lists_controller),
            SmartListsItemMarkUndone(basic_validator, smart_lists_controller),
            SmartListsItemSetTags(basic_validator, smart_lists_controller),
            SmartListsItemSetUrl(basic_validator, smart_lists_controller),
            SmartListsItemShow(basic_validator, smart_lists_controller),
            SmartListsItemHardRemove(basic_validator, smart_lists_controller),
            # Complex commands.
            SyncLocalAndNotion(basic_validator, sync_local_and_notion_controller),
            GenerateInboxTasks(basic_validator, time_provider, generate_inbox_tasks_controller),
            ReportProgress(basic_validator, time_provider, report_progress_controller),
            GarbageCollect(basic_validator, garbage_collect_controller)
        ]

        parser = argparse.ArgumentParser(description=global_properties.description)
        parser.add_argument(
            "--min-log-level", dest="min_log_level", default="info",
            choices=["debug", "info", "warning", "error", "critical"],
            help="The logging level to use")
        parser.add_argument(
            "--verbose", dest="verbose_logging", action="store_const", default=False, const=True,
            help="Show more log messages")
        parser.add_argument(
            "--version", dest="just_show_version", action="store_const", default=False, const=True,
            help="Show the version of the application")

        subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-command help")

        for command in commands:
            command_parser = subparsers.add_parser(
                command.name(), help=command.description(), description=command.description())
            command.build_parser(command_parser)

        args = parser.parse_args()

        coloredlogs.install(
            level=_map_log_level_to_log_class(args.min_log_level),
            fmt="%(asctime)s %(name)-12s %(levelname)-6s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")

        if args.just_show_version:
            print(f"{global_properties.description} {global_properties.version}")
            return

        if not args.verbose_logging:
            for handler in logging.root.handlers:
                handler.addFilter(CommandsAndControllersLoggerFilter())

        try:
            for command in commands:
                if args.subparser_name != command.name():
                    continue
                command.run(args)
                break
        except (MissingWorkspaceRepositoryError, MissingNotionConnectionError, MissingWorkspaceScreenError):
            print(f"The Notion connection isn't setup, please run '{WorkspaceInit.name()}' to create a workspace!")
            print(f"For more information checkout: {global_properties.docs_init_workspace_url}")
        except OldTokenForNotionConnectionError:
            print(f"The Notion connection's token has expired, please refresh it with '{WorkspaceSetToken.name()}'")
            print(f"For more information checkout: {global_properties.docs_update_expired_token_url}")
        except (CollectionEntityNotFound, CollectionEntityAlreadyExists) as err:
            print(str(err))
            print(f"For more information checkout: {global_properties.docs_fix_data_inconsistencies_url}")
            raise err


class CommandsAndControllersLoggerFilter(logging.Filter):
    """A filter for commands and controllers."""

    def filter(self, record: logging.LogRecord) -> int:
        """Filtering the log records for commands and controllers."""
        if record.name.startswith("command.") or record.name.startswith("controllers."):
            return 1
        return 0


def _build_global_properties(workspace_repository: WorkspaceRepository) -> GlobalProperties:
    config_path = Path(os.path.realpath(Path(os.path.realpath(__file__)).parent / ".." / "Config"))

    if not config_path.exists():
        raise Exception("Critical error - missing Config file")

    dotenv.load_dotenv(dotenv_path=config_path, verbose=True)

    description = cast(str, os.getenv("DESCRIPTION"))
    version = cast(str, os.getenv("VERSION"))
    docs_init_workspace_url = cast(str, os.getenv("DOCS_INIT_WORKSPACE_URL"))
    docs_update_expired_token_url = cast(str, os.getenv("DOCS_UPDATE_EXPIRED_TOKEN_URL"))
    docs_fix_data_inconsistencies_url = cast(str, os.getenv("DOCS_FIX_DATA_INCONSISTENCIES_URL"))

    try:
        workspace = workspace_repository.load_workspace()
        timezone = workspace.timezone
    except MissingWorkspaceRepositoryError:
        timezone = pendulum.timezone(os.getenv("TZ", "UTC"))

    return GlobalProperties(
        description=description,
        version=version,
        timezone=timezone,
        docs_init_workspace_url=docs_init_workspace_url,
        docs_update_expired_token_url=docs_update_expired_token_url,
        docs_fix_data_inconsistencies_url=docs_fix_data_inconsistencies_url)


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
