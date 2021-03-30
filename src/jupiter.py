"""The CLI entry-point for Jupiter."""
import argparse
import logging

import coloredlogs

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
from command.metric_archive import MetricArchive
from command.metric_create import MetricCreate
from command.metric_entry_archive import MetricEntryArchive
from command.metric_entry_create import MetricEntryCreate
from command.metric_entry_remove import MetricEntryRemove
from command.metric_entry_update import MetricEntryUpdate
from command.metric_update import MetricUpdate
from command.metric_remove import MetricRemove
from command.metric_show import MetricShow
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
from command.smart_list_archive import SmartListArchive
from command.smart_list_item_update import SmartListItemUpdate
from command.smart_list_remove import SmartListsRemove
from command.smart_list_item_archive import SmartListItemArchive
from command.smart_list_item_create import SmartListItemCreate
from command.smart_list_create import SmartListCreate
from command.smart_list_item_remove import SmartListItemRemove
from command.smart_list_tag_update import SmartListTagUpdate
from command.smart_list_update import SmartListUpdate
from command.smart_list_show import SmartListShow
from command.smart_list_tag_archive import SmartListTagArchive
from command.smart_list_tag_create import SmartListTagCreate
from command.smart_list_tag_remove import SmartListTagRemove
from command.sync_local_and_notion import SyncLocalAndNotion
from command.vacation_archive import VacationArchive
from command.vacation_create import VacationCreate
from command.vacation_remove import VacationRemove
from command.vacation_update import VacationUpdate
from command.vacation_show import VacationsShow
from command.workspace_init import WorkspaceInit
from command.workspace_set_default_project import WorkspaceSetDefaultProject
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
from controllers.sync_local_and_notion import SyncLocalAndNotionController
from controllers.workspaces import WorkspacesController
from domain.metrics.commands.metric_archive import MetricArchiveCommand
from domain.metrics.commands.metric_create import MetricCreateCommand
from domain.metrics.commands.metric_entry_archive import MetricEntryArchiveCommand
from domain.metrics.commands.metric_entry_create import MetricEntryCreateCommand
from domain.metrics.commands.metric_entry_remove import MetricEntryRemoveCommand
from domain.metrics.commands.metric_entry_update import MetricEntryUpdateCommand
from domain.metrics.commands.metric_find import MetricFindCommand
from domain.metrics.commands.metric_remove import MetricRemoveCommand
from domain.metrics.commands.metric_update import MetricUpdateCommand
from domain.smart_lists.commands.smart_list_archive import SmartListArchiveCommand
from domain.smart_lists.commands.smart_list_create import SmartListCreateCommand
from domain.smart_lists.commands.smart_list_find import SmartListFindCommand
from domain.smart_lists.commands.smart_list_item_archive import SmartListItemArchiveCommand
from domain.smart_lists.commands.smart_list_item_create import SmartListItemCreateCommand
from domain.smart_lists.commands.smart_list_item_remove import SmartListItemRemoveCommand
from domain.smart_lists.commands.smart_list_item_update import SmartListItemUpdateCommand
from domain.smart_lists.commands.smart_list_remove import SmartListRemoveCommand
from domain.smart_lists.commands.smart_list_tag_archive import SmartListTagArchiveCommand
from domain.smart_lists.commands.smart_list_tag_create import SmartListTagCreateCommand
from domain.smart_lists.commands.smart_list_tag_remove import SmartListTagRemoveCommand
from domain.smart_lists.commands.smart_list_tag_update import SmartListTagUpdateCommand
from domain.smart_lists.commands.smart_list_update import SmartListUpdateCommand
from domain.vacations.commands.vacation_archive import VacationArchiveCommand
from domain.vacations.commands.vacation_create import VacationCreateCommand
from domain.vacations.commands.vacation_find import VacationFindCommand
from domain.vacations.commands.vacation_remove import VacationRemoveCommand
from domain.vacations.commands.vacation_update import VacationUpdateCommand
from models.basic import BasicValidator
from remote.notion.big_plans_manager import NotionBigPlansManager
from remote.notion.common import CollectionEntityNotFound, CollectionEntityAlreadyExists
from remote.notion.inbox_tasks_manager import NotionInboxTasksManager
from remote.notion.infra.collections_manager import CollectionsManager
from remote.notion.infra.connection import \
    MissingNotionConnectionError, OldTokenForNotionConnectionError, NotionConnection
from remote.notion.infra.pages_manager import PagesManager
from remote.notion.metrics_manager import NotionMetricManager
from remote.notion.projects_manager import NotionProjectsManager
from remote.notion.recurring_tasks_manager import NotionRecurringTasksManager
from remote.notion.smart_lists_manager import NotionSmartListsManager
from remote.notion.vacations_manager import NotionVacationsManager
from remote.notion.workspaces import WorkspaceSingleton, MissingWorkspaceScreenError
from repository.big_plans import BigPlansRepository
from repository.inbox_tasks import InboxTasksRepository
from repository.sqlite.metrics import SqliteMetricEngine
from repository.yaml.smart_lists import YamlSmartListEngine
from repository.projects import ProjectsRepository
from repository.recurring_tasks import RecurringTasksRepository
from repository.yaml.vacations import YamlVacationEngine
from repository.workspace import WorkspaceRepository, MissingWorkspaceRepositoryError
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.metrics import MetricsService
from service.smart_lists import SmartListsService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService
from utils.global_properties import build_global_properties
from utils.time_provider import TimeProvider


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    notion_connection = NotionConnection()

    workspaces_repository = WorkspaceRepository(time_provider)
    workspaces_singleton = WorkspaceSingleton(notion_connection)

    try:
        workspace = workspaces_repository.load_workspace()
        timezone = workspace.timezone
    except MissingWorkspaceRepositoryError:
        timezone = None

    global_properties = build_global_properties(timezone)
    basic_validator = BasicValidator(global_properties)

    with ProjectsRepository(time_provider) as projects_repository, \
            InboxTasksRepository(time_provider) as inbox_tasks_repository, \
            RecurringTasksRepository(time_provider) as recurring_tasks_repository, \
            BigPlansRepository(time_provider) as big_plans_repository, \
            PagesManager(time_provider, notion_connection) as pages_manager, \
            CollectionsManager(time_provider, notion_connection) as collections_manager:
        yaml_vacation_engine = YamlVacationEngine(time_provider)
        yaml_smart_list_engine = YamlSmartListEngine(time_provider)

        sqlite_metric_engine = SqliteMetricEngine(SqliteMetricEngine.Config(
            global_properties.sqlite_db_url, global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path))

        notion_vacation_manager = NotionVacationsManager(
            time_provider, basic_validator, collections_manager)
        notion_projects_manager = NotionProjectsManager(pages_manager)
        notion_inbox_tasks_manager = NotionInboxTasksManager(time_provider, basic_validator, collections_manager)
        notion_recurring_tasks_manager = NotionRecurringTasksManager(
            time_provider, basic_validator, collections_manager)
        notion_big_plans_manager = NotionBigPlansManager(time_provider, basic_validator, collections_manager)
        notion_smart_list_manager = NotionSmartListsManager(
            time_provider, basic_validator, pages_manager, collections_manager)
        notion_metric_manager = NotionMetricManager(
            time_provider, basic_validator, pages_manager, collections_manager)

        workspaces_service = WorkspacesService(
            basic_validator, workspaces_repository, workspaces_singleton)
        vacations_service = VacationsService(
            basic_validator, yaml_vacation_engine, notion_vacation_manager)
        projects_service = ProjectsService(
            basic_validator, projects_repository, notion_projects_manager)
        inbox_tasks_service = InboxTasksService(
            basic_validator, inbox_tasks_repository, notion_inbox_tasks_manager)
        recurring_tasks_service = RecurringTasksService(
            basic_validator, time_provider, recurring_tasks_repository, notion_recurring_tasks_manager)
        big_plans_service = BigPlansService(
            basic_validator, big_plans_repository, notion_big_plans_manager)
        smart_lists_service = SmartListsService(
            basic_validator, time_provider, yaml_smart_list_engine, notion_smart_list_manager)
        metrics_service = MetricsService(
            basic_validator, time_provider, sqlite_metric_engine, notion_metric_manager)

        workspaces_controller = WorkspacesController(
            notion_connection, workspaces_service, vacations_service, projects_service, smart_lists_service,
            metrics_service)
        projects_controller = ProjectsController(
            workspaces_service, projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service,
            metrics_service)
        inbox_tasks_controller = InboxTasksController(
            projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service)
        recurring_tasks_controller = RecurringTasksController(
            global_properties, projects_service, inbox_tasks_service, recurring_tasks_service)
        big_plans_controller = BigPlansController(projects_service, inbox_tasks_service, big_plans_service)
        sync_local_and_notion_controller = SyncLocalAndNotionController(
            time_provider, global_properties, workspaces_service, vacations_service, projects_service,
            inbox_tasks_service, recurring_tasks_service, big_plans_service, smart_lists_service, metrics_service)
        generate_inbox_tasks_controller = GenerateInboxTasksController(
            global_properties, workspaces_service, projects_service, vacations_service, inbox_tasks_service,
            recurring_tasks_service, sqlite_metric_engine)
        report_progress_controller = ReportProgressController(
            global_properties, projects_service, inbox_tasks_service, big_plans_service, recurring_tasks_service,
            metrics_service)
        garbage_collect_controller = GarbageCollectNotionController(
            vacations_service, projects_service, inbox_tasks_service, recurring_tasks_service, big_plans_service,
            smart_lists_service, metrics_service)

        commands = {
            # CRUD Commands
            WorkspaceInit(basic_validator, workspaces_controller),
            WorkspaceSetName(basic_validator, workspaces_controller),
            WorkspaceSetTimezone(basic_validator, workspaces_controller),
            WorkspaceSetDefaultProject(basic_validator, workspaces_controller),
            WorkspaceSetToken(basic_validator, workspaces_controller),
            WorkspaceShow(workspaces_controller),
            VacationCreate(basic_validator, VacationCreateCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationArchive(basic_validator, VacationArchiveCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationUpdate(basic_validator, VacationUpdateCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationRemove(basic_validator, VacationRemoveCommand(
                yaml_vacation_engine, notion_vacation_manager)),
            VacationsShow(basic_validator, VacationFindCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
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
            SmartListCreate(basic_validator, SmartListCreateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListArchive(basic_validator, SmartListArchiveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListUpdate(basic_validator, SmartListUpdateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListShow(basic_validator, SmartListFindCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListsRemove(basic_validator, SmartListRemoveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagCreate(basic_validator, SmartListTagCreateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagArchive(basic_validator, SmartListTagArchiveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagUpdate(basic_validator, SmartListTagUpdateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagRemove(basic_validator, SmartListTagRemoveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemCreate(basic_validator, SmartListItemCreateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemArchive(basic_validator, SmartListItemArchiveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemUpdate(basic_validator, SmartListItemUpdateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemRemove(basic_validator, SmartListItemRemoveCommand(
                yaml_smart_list_engine, notion_smart_list_manager)),
            MetricCreate(basic_validator, MetricCreateCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager, workspaces_service, projects_service)),
            MetricArchive(basic_validator, MetricArchiveCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager, inbox_tasks_service)),
            MetricUpdate(basic_validator, MetricUpdateCommand(
                global_properties, time_provider, basic_validator, sqlite_metric_engine, notion_metric_manager,
                workspaces_service, projects_service, inbox_tasks_service)),
            MetricShow(basic_validator, MetricFindCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager, projects_service, inbox_tasks_service)),
            MetricRemove(basic_validator, MetricRemoveCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager, inbox_tasks_service)),
            MetricEntryCreate(basic_validator, MetricEntryCreateCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryArchive(basic_validator, MetricEntryArchiveCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryUpdate(basic_validator, MetricEntryUpdateCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryRemove(basic_validator, MetricEntryRemoveCommand(
                sqlite_metric_engine, notion_metric_manager)),
            # Complex commands.
            SyncLocalAndNotion(basic_validator, sync_local_and_notion_controller),
            GenerateInboxTasks(basic_validator, time_provider, generate_inbox_tasks_controller),
            ReportProgress(basic_validator, time_provider, report_progress_controller),
            GarbageCollect(basic_validator, garbage_collect_controller)
        }

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

        sqlite_metric_engine.prepare()

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
