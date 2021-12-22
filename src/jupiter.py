"""The CLI entry-point for Jupiter."""
import argparse
import logging
from typing import Optional

import coloredlogs

from command.big_plan_archive import BigPlanArchive
from command.big_plan_create import BigPlanCreate
from command.big_plan_remove import BigPlanRemove
from command.big_plan_show import BigPlanShow
from command.big_plan_update import BigPlanUpdate
from command.gc import GC
from command.gen import Gen
from command.inbox_task_archive import InboxTaskArchive
from command.inbox_task_associate_with_big_plan import InboxTaskAssociateWithBigPlan
from command.inbox_task_create import InboxTaskCreate
from command.inbox_task_remove import InboxTaskRemove
from command.inbox_task_show import InboxTaskShow
from command.inbox_task_update import InboxTaskUpdate
from command.initialize import Initialize
from command.metric_archive import MetricArchive
from command.metric_create import MetricCreate
from command.metric_entry_archive import MetricEntryArchive
from command.metric_entry_create import MetricEntryCreate
from command.metric_entry_remove import MetricEntryRemove
from command.metric_entry_update import MetricEntryUpdate
from command.metric_remove import MetricRemove
from command.metric_show import MetricShow
from command.metric_update import MetricUpdate
from command.person_archive import PersonArchive
from command.person_create import PersonCreate
from command.person_remove import PersonRemove
from command.person_update import PersonUpdate
from command.prm_show import PrmShow
from command.prm_update import PrmUpdate
from command.project_archive import ProjectArchive
from command.project_create import ProjectCreate
from command.project_show import ProjectShow
from command.project_update import ProjectUpdate
from command.recurring_task_archive import RecurringTaskArchive
from command.recurring_task_create import RecurringTaskCreate
from command.recurring_task_remove import RecurringTaskRemove
from command.recurring_task_show import RecurringTaskShow
from command.recurring_task_suspend import RecurringTaskSuspend
from command.recurring_task_unsuspend import RecurringTaskUnsuspend
from command.recurring_task_update import RecurringTaskUpdate
from command.report import Report
from command.smart_list_archive import SmartListArchive
from command.smart_list_create import SmartListCreate
from command.smart_list_item_archive import SmartListItemArchive
from command.smart_list_item_create import SmartListItemCreate
from command.smart_list_item_remove import SmartListItemRemove
from command.smart_list_item_update import SmartListItemUpdate
from command.smart_list_remove import SmartListsRemove
from command.smart_list_show import SmartListShow
from command.smart_list_tag_archive import SmartListTagArchive
from command.smart_list_tag_create import SmartListTagCreate
from command.smart_list_tag_remove import SmartListTagRemove
from command.smart_list_tag_update import SmartListTagUpdate
from command.smart_list_update import SmartListUpdate
from command.sync import Sync
from command.vacation_archive import VacationArchive
from command.vacation_create import VacationCreate
from command.vacation_remove import VacationRemove
from command.vacation_show import VacationsShow
from command.vacation_update import VacationUpdate
from command.workspace_show import WorkspaceShow
from command.workspace_update import WorkspaceUpdate
from domain.timezone import Timezone
from remote.notion.big_plans_manager import NotionBigPlansManager
from remote.notion.common import CollectionEntityNotFound, CollectionEntityAlreadyExists
from remote.notion.inbox_tasks_manager import NotionInboxTasksManager
from remote.notion.infra.collections_manager import CollectionsManager
from remote.notion.infra.connection import \
    MissingNotionConnectionError, OldTokenForNotionConnectionError, NotionConnection
from remote.notion.infra.pages_manager import PagesManager
from remote.notion.metrics_manager import NotionMetricManager
from remote.notion.prm_manager import NotionPrmManager
from remote.notion.projects_manager import NotionProjectsManager
from remote.notion.recurring_tasks_manager import NotionRecurringTasksManager
from remote.notion.smart_lists_manager import NotionSmartListsManager
from remote.notion.vacations_manager import NotionVacationsManager
from remote.notion.workspaces_manager import NotionWorkspacesManager, MissingWorkspaceScreenError
from repository.sqlite.metrics import SqliteMetricEngine
from repository.sqlite.prm import SqlitePrmEngine
from repository.yaml.big_plans import YamlBigPlanEngine
from repository.yaml.inbox_tasks import YamlInboxTaskEngine
from repository.yaml.projects import YamlProjectEngine
from repository.yaml.recurring_tasks import YamlRecurringTaskEngine
from repository.yaml.smart_lists import YamlSmartListEngine
from repository.yaml.vacations import YamlVacationEngine
from repository.yaml.workspace import YamlWorkspaceRepository, MissingWorkspaceRepositoryError, YamlWorkspaceEngine
from use_cases.big_plans.archive import BigPlanArchiveCommand
from use_cases.big_plans.create import BigPlanCreateCommand
from use_cases.big_plans.find import BigPlanFindCommand
from use_cases.big_plans.remove import BigPlanRemoveCommand
from use_cases.big_plans.update import BigPlanUpdateCommand
from use_cases.gc import GCCommand
from use_cases.gen import GenCommand
from use_cases.inbox_tasks.archive import InboxTaskArchiveCommand
from use_cases.inbox_tasks.associate_with_big_plan import InboxTaskAssociateWithBigPlanCommand
from use_cases.inbox_tasks.create import InboxTaskCreateCommand
from use_cases.inbox_tasks.find import InboxTaskFindCommand
from use_cases.inbox_tasks.remove import InboxTaskRemoveCommand
from use_cases.inbox_tasks.update import InboxTaskUpdateCommand
from use_cases.init import InitCommand
from use_cases.metrics.archive import MetricArchiveCommand
from use_cases.metrics.create import MetricCreateCommand
from use_cases.metrics.entry.archive import MetricEntryArchiveCommand
from use_cases.metrics.entry.create import MetricEntryCreateCommand
from use_cases.metrics.entry.remove import MetricEntryRemoveCommand
from use_cases.metrics.entry.update import MetricEntryUpdateCommand
from use_cases.metrics.find import MetricFindCommand
from use_cases.metrics.remove import MetricRemoveCommand
from use_cases.metrics.update import MetricUpdateCommand
from use_cases.prm.find import PrmDatabaseFindCommand
from use_cases.prm.person.archive import PersonArchiveCommand
from use_cases.prm.person.create import PersonCreateCommand
from use_cases.prm.person.remove import PersonRemoveCommand
from use_cases.prm.person.update import PersonUpdateCommand
from use_cases.prm.update import PrmDatabaseUpdateCommand
from use_cases.projects.archive import ProjectArchiveCommand
from use_cases.projects.create import ProjectCreateCommand
from use_cases.projects.find import ProjectFindCommand
from use_cases.projects.update import ProjectUpdateCommand
from use_cases.recurring_tasks.archive import RecurringTaskArchiveCommand
from use_cases.recurring_tasks.create import RecurringTaskCreateCommand
from use_cases.recurring_tasks.find import RecurringTaskFindCommand
from use_cases.recurring_tasks.remove import RecurringTaskRemoveCommand
from use_cases.recurring_tasks.suspend import RecurringTaskSuspendCommand
from use_cases.recurring_tasks.update import RecurringTaskUpdateCommand
from use_cases.report import ReportCommand
from use_cases.smart_lists.archive import SmartListArchiveCommand
from use_cases.smart_lists.create import SmartListCreateCommand
from use_cases.smart_lists.find import SmartListFindCommand
from use_cases.smart_lists.item.archive import SmartListItemArchiveCommand
from use_cases.smart_lists.item.create import SmartListItemCreateCommand
from use_cases.smart_lists.item.remove import SmartListItemRemoveCommand
from use_cases.smart_lists.item.update import SmartListItemUpdateCommand
from use_cases.smart_lists.remove import SmartListRemoveCommand
from use_cases.smart_lists.tag.archive import SmartListTagArchiveCommand
from use_cases.smart_lists.tag.create import SmartListTagCreateCommand
from use_cases.smart_lists.tag.remove import SmartListTagRemoveCommand
from use_cases.smart_lists.tag.update import SmartListTagUpdateCommand
from use_cases.smart_lists.update import SmartListUpdateCommand
from use_cases.sync import SyncCommand
from use_cases.vacations.archive import VacationArchiveCommand
from use_cases.vacations.create import VacationCreateCommand
from use_cases.vacations.find import VacationFindCommand
from use_cases.vacations.remove import VacationRemoveCommand
from use_cases.vacations.update import VacationUpdateCommand
from use_cases.workspaces.find import WorkspaceFindCommand
from use_cases.workspaces.update import WorkspaceUpdateCommand
from utils.global_properties import build_global_properties
from utils.time_provider import TimeProvider


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    notion_connection = NotionConnection()

    workspaces_repository = YamlWorkspaceRepository(time_provider)
    notion_workspace_manager = NotionWorkspacesManager(notion_connection)

    timezone: Optional[Timezone] = None
    try:
        workspace = workspaces_repository.load()
        timezone = workspace.timezone
    except MissingWorkspaceRepositoryError:
        timezone = None

    global_properties = build_global_properties(timezone)

    with PagesManager(time_provider, notion_connection) as pages_manager, \
            CollectionsManager(time_provider, notion_connection) as collections_manager:
        yaml_workspace_engine = YamlWorkspaceEngine(time_provider)
        yaml_project_engine = YamlProjectEngine(time_provider)
        yaml_vacation_engine = YamlVacationEngine(time_provider)
        yaml_inbox_task_engine = YamlInboxTaskEngine(time_provider)
        yaml_recurring_task_engine = YamlRecurringTaskEngine(time_provider)
        yaml_big_plan_engine = YamlBigPlanEngine(time_provider)
        yaml_smart_list_engine = YamlSmartListEngine(time_provider)

        sqlite_metric_engine = SqliteMetricEngine(SqliteMetricEngine.Config(
            global_properties.sqlite_db_url, global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path))
        sqlite_prm_engine = SqlitePrmEngine(SqlitePrmEngine.Config(
            global_properties.sqlite_db_url, global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path))

        notion_vacation_manager = NotionVacationsManager(
            global_properties, time_provider, collections_manager)
        notion_projects_manager = NotionProjectsManager(pages_manager)
        notion_inbox_tasks_manager = NotionInboxTasksManager(global_properties, time_provider, collections_manager)
        notion_recurring_tasks_manager = NotionRecurringTasksManager(
            global_properties, time_provider, collections_manager)
        notion_big_plans_manager = NotionBigPlansManager(global_properties, time_provider, collections_manager)
        notion_smart_list_manager = NotionSmartListsManager(
            global_properties, time_provider, pages_manager, collections_manager)
        notion_metric_manager = NotionMetricManager(
            global_properties, time_provider, pages_manager, collections_manager)
        notion_prm_manager = NotionPrmManager(global_properties, time_provider, collections_manager)

        commands = {
            # Complex commands.
            Initialize(InitCommand(
                time_provider, notion_connection, yaml_workspace_engine, notion_workspace_manager,
                notion_vacation_manager, yaml_project_engine, notion_projects_manager,
                notion_smart_list_manager, notion_metric_manager, sqlite_prm_engine,
                notion_prm_manager)),
            Sync(SyncCommand(
                global_properties, time_provider, yaml_workspace_engine, notion_workspace_manager,
                yaml_vacation_engine, notion_vacation_manager, yaml_project_engine,
                notion_projects_manager, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                yaml_recurring_task_engine, notion_recurring_tasks_manager, yaml_big_plan_engine,
                notion_big_plans_manager, yaml_smart_list_engine, notion_smart_list_manager,
                sqlite_metric_engine, notion_metric_manager, sqlite_prm_engine, notion_prm_manager)),
            Gen(global_properties, time_provider,
                GenCommand(
                    global_properties, time_provider, yaml_project_engine, yaml_vacation_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_recurring_task_engine, sqlite_metric_engine, sqlite_prm_engine)),
            Report(
                global_properties, time_provider,
                ReportCommand(
                    global_properties, yaml_project_engine, yaml_inbox_task_engine,
                    yaml_recurring_task_engine, yaml_big_plan_engine, sqlite_metric_engine, sqlite_prm_engine)),
            GC(GCCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager, yaml_project_engine,
                yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_recurring_task_engine,
                notion_recurring_tasks_manager, yaml_big_plan_engine, notion_big_plans_manager,
                yaml_smart_list_engine, notion_smart_list_manager, sqlite_metric_engine, notion_metric_manager,
                sqlite_prm_engine, notion_prm_manager)),
            # CRUD Commands.
            WorkspaceUpdate(notion_connection, WorkspaceUpdateCommand(
                time_provider, yaml_workspace_engine, notion_workspace_manager, yaml_project_engine)),
            WorkspaceShow(WorkspaceFindCommand(yaml_workspace_engine, yaml_project_engine)),
            VacationCreate(global_properties, VacationCreateCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationArchive(VacationArchiveCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationUpdate(global_properties, VacationUpdateCommand(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationRemove(VacationRemoveCommand(
                yaml_vacation_engine, notion_vacation_manager)),
            VacationsShow(global_properties, VacationFindCommand(yaml_vacation_engine)),
            ProjectCreate(ProjectCreateCommand(
                time_provider, yaml_project_engine, notion_projects_manager,
                yaml_inbox_task_engine, notion_inbox_tasks_manager,
                yaml_recurring_task_engine, notion_recurring_tasks_manager,
                yaml_big_plan_engine, notion_big_plans_manager)),
            ProjectUpdate(ProjectUpdateCommand(
                time_provider, yaml_project_engine, notion_projects_manager)),
            ProjectArchive(ProjectArchiveCommand(
                time_provider, yaml_workspace_engine, yaml_project_engine, notion_projects_manager,
                yaml_inbox_task_engine, notion_inbox_tasks_manager,
                yaml_recurring_task_engine, notion_recurring_tasks_manager,
                yaml_big_plan_engine, notion_big_plans_manager, sqlite_metric_engine, sqlite_prm_engine)),
            ProjectShow(ProjectFindCommand(yaml_project_engine)),
            InboxTaskCreate(
                global_properties,
                InboxTaskCreateCommand(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_big_plan_engine)),
            InboxTaskArchive(
                InboxTaskArchiveCommand(time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager)),
            InboxTaskAssociateWithBigPlan(
                InboxTaskAssociateWithBigPlanCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_big_plan_engine)),
            InboxTaskRemove(
                InboxTaskRemoveCommand(time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager)),
            InboxTaskUpdate(
                global_properties,
                InboxTaskUpdateCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_big_plan_engine)),
            InboxTaskShow(
                global_properties,
                InboxTaskFindCommand(
                    yaml_project_engine, yaml_inbox_task_engine, yaml_recurring_task_engine, yaml_big_plan_engine,
                    sqlite_metric_engine, sqlite_prm_engine)),
            RecurringTaskCreate(
                global_properties,
                RecurringTaskCreateCommand(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskArchive(
                RecurringTaskArchiveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_recurring_task_engine,
                    notion_recurring_tasks_manager)),
            RecurringTaskSuspend(
                RecurringTaskSuspendCommand(
                    time_provider, yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskUnsuspend(
                RecurringTaskSuspendCommand(time_provider, yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskRemove(
                RecurringTaskRemoveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskUpdate(
                global_properties,
                RecurringTaskUpdateCommand(
                    global_properties, time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskShow(
                global_properties,
                RecurringTaskFindCommand(
                    yaml_project_engine, yaml_inbox_task_engine, yaml_recurring_task_engine)),
            BigPlanCreate(
                global_properties,
                BigPlanCreateCommand(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanArchive(
                BigPlanArchiveCommand(
                    time_provider, yaml_project_engine, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanRemove(
                BigPlanRemoveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanUpdate(
                global_properties,
                BigPlanUpdateCommand(
                    time_provider, yaml_project_engine, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanShow(
                global_properties,
                BigPlanFindCommand(yaml_project_engine, yaml_inbox_task_engine, yaml_big_plan_engine)),
            SmartListCreate(SmartListCreateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListArchive(SmartListArchiveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListUpdate(SmartListUpdateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListShow(SmartListFindCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListsRemove(SmartListRemoveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagCreate(SmartListTagCreateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagArchive(SmartListTagArchiveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagUpdate(SmartListTagUpdateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagRemove(SmartListTagRemoveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemCreate(SmartListItemCreateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemArchive(SmartListItemArchiveCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemUpdate(SmartListItemUpdateCommand(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemRemove(SmartListItemRemoveCommand(
                yaml_smart_list_engine, notion_smart_list_manager)),
            MetricCreate(
                MetricCreateCommand(
                    time_provider, sqlite_metric_engine, notion_metric_manager, yaml_workspace_engine,
                    yaml_project_engine)),
            MetricArchive(
                MetricArchiveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, sqlite_metric_engine,
                    notion_metric_manager)),
            MetricUpdate(
                MetricUpdateCommand(
                    global_properties, time_provider, yaml_workspace_engine, yaml_project_engine,
                    yaml_inbox_task_engine, notion_inbox_tasks_manager, sqlite_metric_engine, notion_metric_manager)),
            MetricShow(
                global_properties,
                MetricFindCommand(
                    yaml_project_engine, yaml_inbox_task_engine, sqlite_metric_engine)),
            MetricRemove(
                MetricRemoveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    sqlite_metric_engine, notion_metric_manager)),
            MetricEntryCreate(MetricEntryCreateCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryArchive(MetricEntryArchiveCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryUpdate(MetricEntryUpdateCommand(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryRemove(MetricEntryRemoveCommand(
                sqlite_metric_engine, notion_metric_manager)),
            PrmUpdate(
                PrmDatabaseUpdateCommand(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, sqlite_prm_engine, notion_prm_manager)),
            PrmShow(
                PrmDatabaseFindCommand(
                    sqlite_prm_engine, yaml_project_engine)),
            PersonCreate(
                PersonCreateCommand(
                    time_provider, sqlite_prm_engine, notion_prm_manager)),
            PersonArchive(
                PersonArchiveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    sqlite_prm_engine, notion_prm_manager)),
            PersonUpdate(
                PersonUpdateCommand(
                    global_properties, time_provider, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, sqlite_prm_engine, notion_prm_manager)),
            PersonRemove(
                PersonRemoveCommand(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    sqlite_prm_engine, notion_prm_manager))
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
            print(f"The Notion connection isn't setup, please run '{Initialize.name()}' to create a workspace!")
            print(f"For more information checkout: {global_properties.docs_init_workspace_url}")
        except OldTokenForNotionConnectionError:
            print(
                f"The Notion connection's token has expired, please refresh it with '{WorkspaceUpdate.name()}'")
            print(f"For more information checkout: {global_properties.docs_update_expired_token_url}")
        except (CollectionEntityNotFound, CollectionEntityAlreadyExists) as err:
            print(str(err))
            print(f"For more information checkout: {global_properties.docs_fix_data_inconsistencies_url}")
            raise err


class CommandsAndControllersLoggerFilter(logging.Filter):
    """A filter for commands and controllers."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filtering the log records for commands and controllers."""
        if record.name.startswith("command.") or record.name.startswith("controllers."):
            return True
        return False


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
