"""The CLI entry-point for Jupiter."""
import argparse
import logging
from typing import Optional

import coloredlogs

from jupiter.command.big_plan_archive import BigPlanArchive
from jupiter.command.big_plan_create import BigPlanCreate
from jupiter.command.big_plan_remove import BigPlanRemove
from jupiter.command.big_plan_show import BigPlanShow
from jupiter.command.big_plan_update import BigPlanUpdate
from jupiter.command.gc import GC
from jupiter.command.gen import Gen
from jupiter.command.inbox_task_archive import InboxTaskArchive
from jupiter.command.inbox_task_associate_with_big_plan import InboxTaskAssociateWithBigPlan
from jupiter.command.inbox_task_create import InboxTaskCreate
from jupiter.command.inbox_task_remove import InboxTaskRemove
from jupiter.command.inbox_task_show import InboxTaskShow
from jupiter.command.inbox_task_update import InboxTaskUpdate
from jupiter.command.initialize import Initialize
from jupiter.command.metric_archive import MetricArchive
from jupiter.command.metric_create import MetricCreate
from jupiter.command.metric_entry_archive import MetricEntryArchive
from jupiter.command.metric_entry_create import MetricEntryCreate
from jupiter.command.metric_entry_remove import MetricEntryRemove
from jupiter.command.metric_entry_update import MetricEntryUpdate
from jupiter.command.metric_remove import MetricRemove
from jupiter.command.metric_show import MetricShow
from jupiter.command.metric_update import MetricUpdate
from jupiter.command.person_archive import PersonArchive
from jupiter.command.person_create import PersonCreate
from jupiter.command.person_remove import PersonRemove
from jupiter.command.person_update import PersonUpdate
from jupiter.command.prm_show import PrmShow
from jupiter.command.prm_update import PrmUpdate
from jupiter.command.project_archive import ProjectArchive
from jupiter.command.project_create import ProjectCreate
from jupiter.command.project_show import ProjectShow
from jupiter.command.project_update import ProjectUpdate
from jupiter.command.recurring_task_archive import RecurringTaskArchive
from jupiter.command.recurring_task_create import RecurringTaskCreate
from jupiter.command.recurring_task_remove import RecurringTaskRemove
from jupiter.command.recurring_task_show import RecurringTaskShow
from jupiter.command.recurring_task_suspend import RecurringTaskSuspend
from jupiter.command.recurring_task_unsuspend import RecurringTaskUnsuspend
from jupiter.command.recurring_task_update import RecurringTaskUpdate
from jupiter.command.report import Report
from jupiter.command.smart_list_archive import SmartListArchive
from jupiter.command.smart_list_create import SmartListCreate
from jupiter.command.smart_list_item_archive import SmartListItemArchive
from jupiter.command.smart_list_item_create import SmartListItemCreate
from jupiter.command.smart_list_item_remove import SmartListItemRemove
from jupiter.command.smart_list_item_update import SmartListItemUpdate
from jupiter.command.smart_list_remove import SmartListsRemove
from jupiter.command.smart_list_show import SmartListShow
from jupiter.command.smart_list_tag_archive import SmartListTagArchive
from jupiter.command.smart_list_tag_create import SmartListTagCreate
from jupiter.command.smart_list_tag_remove import SmartListTagRemove
from jupiter.command.smart_list_tag_update import SmartListTagUpdate
from jupiter.command.smart_list_update import SmartListUpdate
from jupiter.command.sync import Sync
from jupiter.command.vacation_archive import VacationArchive
from jupiter.command.vacation_create import VacationCreate
from jupiter.command.vacation_remove import VacationRemove
from jupiter.command.vacation_show import VacationsShow
from jupiter.command.vacation_update import VacationUpdate
from jupiter.command.workspace_show import WorkspaceShow
from jupiter.command.workspace_update import WorkspaceUpdate
from jupiter.domain.big_plans.infra.big_plan_notion_manager import NotionBigPlanNotFoundError
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import NotionInboxTaskNotFoundError
from jupiter.domain.metrics.infra.metric_notion_manager import NotionMetricNotFoundError, NotionMetricEntryNotFoundError
from jupiter.domain.prm.infra.prm_notion_manager import NotionPersonNotFoundError
from jupiter.domain.projects.infra.project_notion_manager import NotionProjectNotFoundError
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import NotionRecurringTaskNotFoundError
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import NotionSmartListNotFoundError, \
    NotionSmartListTagNotFoundError, NotionSmartListItemNotFoundError
from jupiter.domain.timezone import Timezone
from jupiter.domain.vacations.infra.vacation_notion_manager import NotionVacationNotFoundError
from jupiter.domain.workspaces.infra.workspace_notion_manager import NotionWorkspaceNotFoundError
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceNotFoundError
from jupiter.framework.errors import InputValidationError
from jupiter.remote.notion.big_plans_manager import NotionBigPlansManager
from jupiter.remote.notion.inbox_tasks_manager import NotionInboxTasksManager
from jupiter.remote.notion.infra.collections_manager import CollectionsManager
from jupiter.remote.notion.infra.connection import \
    MissingNotionConnectionError, OldTokenForNotionConnectionError, NotionConnection
from jupiter.remote.notion.infra.pages_manager import PagesManager
from jupiter.remote.notion.metrics_manager import NotionMetricManager
from jupiter.remote.notion.prm_manager import NotionPrmManager
from jupiter.remote.notion.projects_manager import NotionProjectsManager
from jupiter.remote.notion.recurring_tasks_manager import NotionRecurringTasksManager
from jupiter.remote.notion.smart_lists_manager import NotionSmartListsManager
from jupiter.remote.notion.vacations_manager import NotionVacationsManager
from jupiter.remote.notion.workspaces_manager import NotionWorkspacesManager
from jupiter.repository.sqlite.metrics import SqliteMetricEngine
from jupiter.repository.sqlite.prm import SqlitePrmEngine
from jupiter.repository.yaml.big_plans import YamlBigPlanEngine
from jupiter.repository.yaml.inbox_tasks import YamlInboxTaskEngine
from jupiter.repository.yaml.projects import YamlProjectEngine
from jupiter.repository.yaml.recurring_tasks import YamlRecurringTaskEngine
from jupiter.repository.yaml.smart_lists import YamlSmartListEngine
from jupiter.repository.yaml.vacations import YamlVacationEngine
from jupiter.repository.yaml.workspace import YamlWorkspaceRepository, YamlWorkspaceEngine
from jupiter.use_cases.big_plans.archive import BigPlanArchiveUseCase
from jupiter.use_cases.big_plans.create import BigPlanCreateUseCase
from jupiter.use_cases.big_plans.find import BigPlanFindUseCase
from jupiter.use_cases.big_plans.remove import BigPlanRemoveUseCase
from jupiter.use_cases.big_plans.update import BigPlanUpdateUseCase
from jupiter.use_cases.gc import GCUseCase
from jupiter.use_cases.gen import GenUseCase
from jupiter.use_cases.inbox_tasks.archive import InboxTaskArchiveUseCase
from jupiter.use_cases.inbox_tasks.associate_with_big_plan import InboxTaskAssociateWithBigPlanUseCase
from jupiter.use_cases.inbox_tasks.create import InboxTaskCreateUseCase
from jupiter.use_cases.inbox_tasks.find import InboxTaskFindUseCase
from jupiter.use_cases.inbox_tasks.remove import InboxTaskRemoveUseCase
from jupiter.use_cases.inbox_tasks.update import InboxTaskUpdateUseCase
from jupiter.use_cases.init import InitUseCase
from jupiter.use_cases.metrics.archive import MetricArchiveUseCase
from jupiter.use_cases.metrics.create import MetricCreateUseCase
from jupiter.use_cases.metrics.entry.archive import MetricEntryArchiveUseCase
from jupiter.use_cases.metrics.entry.create import MetricEntryCreateUseCase
from jupiter.use_cases.metrics.entry.remove import MetricEntryRemoveUseCase
from jupiter.use_cases.metrics.entry.update import MetricEntryUpdateUseCase
from jupiter.use_cases.metrics.find import MetricFindUseCase
from jupiter.use_cases.metrics.remove import MetricRemoveUseCase
from jupiter.use_cases.metrics.update import MetricUpdateUseCase
from jupiter.use_cases.prm.find import PrmDatabaseFindUseCase
from jupiter.use_cases.prm.person.archive import PersonArchiveUseCase
from jupiter.use_cases.prm.person.create import PersonCreateUseCase
from jupiter.use_cases.prm.person.remove import PersonRemoveUseCase
from jupiter.use_cases.prm.person.update import PersonUpdateUseCase
from jupiter.use_cases.prm.update import PrmDatabaseUpdateUseCase
from jupiter.use_cases.projects.archive import ProjectArchiveUseCase
from jupiter.use_cases.projects.create import ProjectCreateUseCase
from jupiter.use_cases.projects.find import ProjectFindUseCase
from jupiter.use_cases.projects.update import ProjectUpdateUseCase
from jupiter.use_cases.recurring_tasks.archive import RecurringTaskArchiveUseCase
from jupiter.use_cases.recurring_tasks.create import RecurringTaskCreateUseCase
from jupiter.use_cases.recurring_tasks.find import RecurringTaskFindUseCase
from jupiter.use_cases.recurring_tasks.remove import RecurringTaskRemoveUseCase
from jupiter.use_cases.recurring_tasks.suspend import RecurringTaskSuspendUseCase
from jupiter.use_cases.recurring_tasks.update import RecurringTaskUpdateUseCase
from jupiter.use_cases.report import ReportUseCase
from jupiter.use_cases.smart_lists.archive import SmartListArchiveUseCase
from jupiter.use_cases.smart_lists.create import SmartListCreateUseCase
from jupiter.use_cases.smart_lists.find import SmartListFindUseCase
from jupiter.use_cases.smart_lists.item.archive import SmartListItemArchiveUseCase
from jupiter.use_cases.smart_lists.item.create import SmartListItemCreateUseCase
from jupiter.use_cases.smart_lists.item.remove import SmartListItemRemoveUseCase
from jupiter.use_cases.smart_lists.item.update import SmartListItemUpdateUseCase
from jupiter.use_cases.smart_lists.remove import SmartListRemoveUseCase
from jupiter.use_cases.smart_lists.tag.archive import SmartListTagArchiveUseCase
from jupiter.use_cases.smart_lists.tag.create import SmartListTagCreateUseCase
from jupiter.use_cases.smart_lists.tag.remove import SmartListTagRemoveUseCase
from jupiter.use_cases.smart_lists.tag.update import SmartListTagUpdateUseCase
from jupiter.use_cases.smart_lists.update import SmartListUpdateUseCase
from jupiter.use_cases.sync import SyncUseCase
from jupiter.use_cases.vacations.archive import VacationArchiveUseCase
from jupiter.use_cases.vacations.create import VacationCreateUseCase
from jupiter.use_cases.vacations.find import VacationFindUseCase
from jupiter.use_cases.vacations.remove import VacationRemoveUseCase
from jupiter.use_cases.vacations.update import VacationUpdateUseCase
from jupiter.use_cases.workspaces.find import WorkspaceFindUseCase
from jupiter.use_cases.workspaces.update import WorkspaceUpdateUseCase
from jupiter.utils.global_properties import build_global_properties
from jupiter.utils.time_provider import TimeProvider


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
    except WorkspaceNotFoundError:
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
            Initialize(InitUseCase(
                time_provider, notion_connection, yaml_workspace_engine, notion_workspace_manager,
                notion_vacation_manager, yaml_project_engine, notion_projects_manager,
                notion_smart_list_manager, notion_metric_manager, sqlite_prm_engine,
                notion_prm_manager)),
            Sync(SyncUseCase(
                global_properties, time_provider, yaml_workspace_engine, notion_workspace_manager,
                yaml_vacation_engine, notion_vacation_manager, yaml_project_engine,
                notion_projects_manager, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                yaml_recurring_task_engine, notion_recurring_tasks_manager, yaml_big_plan_engine,
                notion_big_plans_manager, yaml_smart_list_engine, notion_smart_list_manager,
                sqlite_metric_engine, notion_metric_manager, sqlite_prm_engine, notion_prm_manager)),
            Gen(global_properties, time_provider,
                GenUseCase(
                    global_properties, time_provider, yaml_project_engine, yaml_vacation_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_recurring_task_engine, sqlite_metric_engine, sqlite_prm_engine)),
            Report(
                global_properties, time_provider,
                ReportUseCase(
                    global_properties, yaml_project_engine, yaml_inbox_task_engine,
                    yaml_recurring_task_engine, yaml_big_plan_engine, sqlite_metric_engine, sqlite_prm_engine)),
            GC(GCUseCase(
                time_provider, yaml_vacation_engine, notion_vacation_manager, yaml_project_engine,
                yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_recurring_task_engine,
                notion_recurring_tasks_manager, yaml_big_plan_engine, notion_big_plans_manager,
                yaml_smart_list_engine, notion_smart_list_manager, sqlite_metric_engine, notion_metric_manager,
                sqlite_prm_engine, notion_prm_manager)),
            # CRUD Commands.
            WorkspaceUpdate(notion_connection, WorkspaceUpdateUseCase(
                time_provider, yaml_workspace_engine, notion_workspace_manager, yaml_project_engine)),
            WorkspaceShow(WorkspaceFindUseCase(yaml_workspace_engine, yaml_project_engine)),
            VacationCreate(global_properties, VacationCreateUseCase(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationArchive(VacationArchiveUseCase(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationUpdate(global_properties, VacationUpdateUseCase(
                time_provider, yaml_vacation_engine, notion_vacation_manager)),
            VacationRemove(VacationRemoveUseCase(
                yaml_vacation_engine, notion_vacation_manager)),
            VacationsShow(global_properties, VacationFindUseCase(yaml_vacation_engine)),
            ProjectCreate(ProjectCreateUseCase(
                time_provider, yaml_project_engine, notion_projects_manager,
                yaml_inbox_task_engine, notion_inbox_tasks_manager,
                yaml_recurring_task_engine, notion_recurring_tasks_manager,
                yaml_big_plan_engine, notion_big_plans_manager)),
            ProjectUpdate(ProjectUpdateUseCase(
                time_provider, yaml_project_engine, notion_projects_manager)),
            ProjectArchive(ProjectArchiveUseCase(
                time_provider, yaml_workspace_engine, yaml_project_engine, notion_projects_manager,
                yaml_inbox_task_engine, notion_inbox_tasks_manager,
                yaml_recurring_task_engine, notion_recurring_tasks_manager,
                yaml_big_plan_engine, notion_big_plans_manager, sqlite_metric_engine, sqlite_prm_engine)),
            ProjectShow(ProjectFindUseCase(yaml_project_engine)),
            InboxTaskCreate(
                global_properties,
                InboxTaskCreateUseCase(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_big_plan_engine)),
            InboxTaskArchive(
                InboxTaskArchiveUseCase(time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager)),
            InboxTaskAssociateWithBigPlan(
                InboxTaskAssociateWithBigPlanUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_big_plan_engine)),
            InboxTaskRemove(
                InboxTaskRemoveUseCase(time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager)),
            InboxTaskUpdate(
                global_properties,
                InboxTaskUpdateUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_big_plan_engine)),
            InboxTaskShow(
                global_properties,
                InboxTaskFindUseCase(
                    yaml_project_engine, yaml_inbox_task_engine, yaml_recurring_task_engine, yaml_big_plan_engine,
                    sqlite_metric_engine, sqlite_prm_engine)),
            RecurringTaskCreate(
                global_properties,
                RecurringTaskCreateUseCase(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskArchive(
                RecurringTaskArchiveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, yaml_recurring_task_engine,
                    notion_recurring_tasks_manager)),
            RecurringTaskSuspend(
                RecurringTaskSuspendUseCase(
                    time_provider, yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskUnsuspend(
                RecurringTaskSuspendUseCase(time_provider, yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskRemove(
                RecurringTaskRemoveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskUpdate(
                global_properties,
                RecurringTaskUpdateUseCase(
                    global_properties, time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_recurring_task_engine, notion_recurring_tasks_manager)),
            RecurringTaskShow(
                global_properties,
                RecurringTaskFindUseCase(
                    yaml_project_engine, yaml_inbox_task_engine, yaml_recurring_task_engine)),
            BigPlanCreate(
                global_properties,
                BigPlanCreateUseCase(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanArchive(
                BigPlanArchiveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanRemove(
                BigPlanRemoveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanUpdate(
                global_properties,
                BigPlanUpdateUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    yaml_big_plan_engine, notion_big_plans_manager)),
            BigPlanShow(
                global_properties,
                BigPlanFindUseCase(yaml_project_engine, yaml_inbox_task_engine, yaml_big_plan_engine)),
            SmartListCreate(SmartListCreateUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListArchive(SmartListArchiveUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListUpdate(SmartListUpdateUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListShow(SmartListFindUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListsRemove(SmartListRemoveUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagCreate(SmartListTagCreateUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagArchive(SmartListTagArchiveUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagUpdate(SmartListTagUpdateUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListTagRemove(SmartListTagRemoveUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemCreate(SmartListItemCreateUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemArchive(SmartListItemArchiveUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemUpdate(SmartListItemUpdateUseCase(
                time_provider, yaml_smart_list_engine, notion_smart_list_manager)),
            SmartListItemRemove(SmartListItemRemoveUseCase(
                yaml_smart_list_engine, notion_smart_list_manager)),
            MetricCreate(
                MetricCreateUseCase(
                    time_provider, sqlite_metric_engine, notion_metric_manager, yaml_workspace_engine,
                    yaml_project_engine)),
            MetricArchive(
                MetricArchiveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager, sqlite_metric_engine,
                    notion_metric_manager)),
            MetricUpdate(
                MetricUpdateUseCase(
                    global_properties, time_provider, yaml_workspace_engine, yaml_project_engine,
                    yaml_inbox_task_engine, notion_inbox_tasks_manager, sqlite_metric_engine, notion_metric_manager)),
            MetricShow(
                global_properties,
                MetricFindUseCase(
                    yaml_project_engine, yaml_inbox_task_engine, sqlite_metric_engine)),
            MetricRemove(
                MetricRemoveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    sqlite_metric_engine, notion_metric_manager)),
            MetricEntryCreate(MetricEntryCreateUseCase(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryArchive(MetricEntryArchiveUseCase(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryUpdate(MetricEntryUpdateUseCase(
                time_provider, sqlite_metric_engine, notion_metric_manager)),
            MetricEntryRemove(MetricEntryRemoveUseCase(
                sqlite_metric_engine, notion_metric_manager)),
            PrmUpdate(
                PrmDatabaseUpdateUseCase(
                    time_provider, yaml_workspace_engine, yaml_project_engine, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, sqlite_prm_engine, notion_prm_manager)),
            PrmShow(
                PrmDatabaseFindUseCase(
                    sqlite_prm_engine, yaml_project_engine)),
            PersonCreate(
                PersonCreateUseCase(
                    time_provider, sqlite_prm_engine, notion_prm_manager)),
            PersonArchive(
                PersonArchiveUseCase(
                    time_provider, yaml_inbox_task_engine, notion_inbox_tasks_manager,
                    sqlite_prm_engine, notion_prm_manager)),
            PersonUpdate(
                PersonUpdateUseCase(
                    global_properties, time_provider, yaml_inbox_task_engine,
                    notion_inbox_tasks_manager, sqlite_prm_engine, notion_prm_manager)),
            PersonRemove(
                PersonRemoveUseCase(
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
        except (WorkspaceNotFoundError, NotionWorkspaceNotFoundError, MissingNotionConnectionError):
            print(f"The Notion connection isn't setup, please run '{Initialize.name()}' to create a workspace!")
            print(f"For more information checkout: {global_properties.docs_init_workspace_url}")
        except OldTokenForNotionConnectionError:
            print(
                f"The Notion connection's token has expired, please refresh it with '{WorkspaceUpdate.name()}'")
            print(f"For more information checkout: {global_properties.docs_update_expired_token_url}")
        except (NotionVacationNotFoundError, NotionProjectNotFoundError,
                NotionInboxTaskNotFoundError, NotionRecurringTaskNotFoundError, NotionBigPlanNotFoundError,
                NotionMetricNotFoundError, NotionMetricEntryNotFoundError,
                NotionSmartListNotFoundError, NotionSmartListTagNotFoundError, NotionSmartListItemNotFoundError,
                NotionPersonNotFoundError) as err:
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
        raise InputValidationError(f"Invalid log level '{log_level}'")


if __name__ == "__main__":
    main()
