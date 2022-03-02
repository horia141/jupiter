"""The service class for syncing inbox tasks."""
import logging
from typing import Final, Iterable, Optional

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project import Project
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.remote.notion.common import format_name_for_option
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskSyncService:
    """The service class for syncing inbox tasks."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def inbox_tasks_sync(
            self,
            workspace: Workspace,
            all_projects: Iterable[Project],
            all_big_plans: Iterable[BigPlan],
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]],
            filter_project_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[InboxTask]:
        """Synchronise the inbox tasks between the Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
            all_inbox_tasks = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_ref_ids=filter_ref_ids, filter_project_ref_ids=filter_project_ref_ids)
        all_inbox_tasks_set = {rt.ref_id: rt for rt in all_inbox_tasks}

        if not drop_all_notion_side:
            all_notion_inbox_tasks = self._inbox_task_notion_manager.load_all_inbox_tasks(inbox_task_collection.ref_id)
            all_notion_inbox_tasks_notion_ids = \
                set(self._inbox_task_notion_manager.load_all_saved_inbox_tasks_notion_ids(inbox_task_collection.ref_id))
        else:
            self._inbox_task_notion_manager.drop_all_inbox_tasks(inbox_task_collection.ref_id)
            all_notion_inbox_tasks = {}
            all_notion_inbox_tasks_notion_ids = set()
        all_notion_inbox_tasks_set = {}

        all_big_plans_by_name = {format_name_for_option(bp.name): bp for bp in all_big_plans}
        all_big_plans_map = {bp.ref_id: bp for bp in all_big_plans}
        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        inverse_info = \
            NotionInboxTask.InverseInfo(
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map,
                all_big_plans_by_name=all_big_plans_by_name,
                all_big_plans_map=all_big_plans_map)

        # Prepare Notion connection

        for notion_inbox_task in all_notion_inbox_tasks:
            # Skip this step when asking only for particular entities to be synced.
            if filter_ref_ids_set is not None and notion_inbox_task.ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{notion_inbox_task.name}' " +
                    f"(id={notion_inbox_task.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_inbox_task.name}' (id={notion_inbox_task.notion_id})")

            if notion_inbox_task.ref_id is None:
                # If the inbox task doesn't exist locally, we create it!
                new_inbox_task = notion_inbox_task.new_entity(inverse_info)

                with self._storage_engine.get_unit_of_work() as save_uow:
                    new_inbox_task = save_uow.inbox_task_repository.create(new_inbox_task)
                LOGGER.info(f"Found new inbox task from Notion {notion_inbox_task.name}")

                self._inbox_task_notion_manager.link_local_and_notion_inbox_task(
                    inbox_task_collection.ref_id, new_inbox_task.ref_id, notion_inbox_task.notion_id)
                LOGGER.info("Linked the new inbox task with local entries")

                direct_info = \
                    NotionInboxTask.DirectInfo(
                        project_name=all_projects_map[new_inbox_task.project_ref_id].name,
                        big_plan_name=
                        all_big_plans_map[new_inbox_task.big_plan_ref_id].name
                        if new_inbox_task.big_plan_ref_id else None)
                notion_inbox_task = \
                    notion_inbox_task.join_with_entity(new_inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(inbox_task_collection.ref_id, notion_inbox_task)
                LOGGER.info(f"Applied changes on Notion side too as {notion_inbox_task}")

                all_inbox_tasks_set[new_inbox_task.ref_id] = new_inbox_task
                all_notion_inbox_tasks_set[new_inbox_task.ref_id] = notion_inbox_task
            elif notion_inbox_task.ref_id in all_inbox_tasks_set and \
                    notion_inbox_task.notion_id in all_notion_inbox_tasks_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                inbox_task = all_inbox_tasks_set[notion_inbox_task.ref_id]
                all_notion_inbox_tasks_set[notion_inbox_task.ref_id] = notion_inbox_task

                if sync_prefer == SyncPrefer.NOTION:
                    # Copy over the parameters from Notion to local
                    if not sync_even_if_not_modified \
                            and notion_inbox_task.last_edited_time <= inbox_task.last_modified_time:
                        LOGGER.info(f"Skipping {notion_inbox_task.name} because it was not modified")
                        continue

                    updated_inbox_task = notion_inbox_task.apply_to_entity(inbox_task, inverse_info)
                    with self._storage_engine.get_unit_of_work() as save_uow:
                        save_uow.inbox_task_repository.save(updated_inbox_task)
                    all_inbox_tasks_set[notion_inbox_task.ref_id] = updated_inbox_task
                    LOGGER.info(f"Changed inbox task with id={notion_inbox_task.ref_id} from Notion")

                    if notion_inbox_task.project_ref_id is None or notion_inbox_task.project_name is None:
                        direct_info = \
                            NotionInboxTask.DirectInfo(
                                project_name=all_projects_map[inbox_task.project_ref_id].name,
                                big_plan_name=
                                all_big_plans_map[
                                    inbox_task.big_plan_ref_id].name if inbox_task.big_plan_ref_id else None)
                        update_notion_inbox_task = \
                            notion_inbox_task.join_with_entity(updated_inbox_task, direct_info)
                        self._inbox_task_notion_manager.save_inbox_task(
                            inbox_task_collection.ref_id, update_notion_inbox_task)
                        LOGGER.info(f"Applies changes on Notion side too as {update_notion_inbox_task}")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            inbox_task.last_modified_time <= notion_inbox_task.last_edited_time:
                        LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                        continue

                    direct_info = \
                        NotionInboxTask.DirectInfo(
                            project_name=all_projects_map[inbox_task.project_ref_id].name,
                            big_plan_name=
                            all_big_plans_map[inbox_task.big_plan_ref_id].name if inbox_task.big_plan_ref_id else None)
                    updated_notion_inbox_task = \
                        notion_inbox_task.join_with_entity(inbox_task, direct_info)
                    self._inbox_task_notion_manager.save_inbox_task(
                        inbox_task_collection.ref_id, updated_notion_inbox_task)
                    all_notion_inbox_tasks_set[notion_inbox_task.ref_id] = updated_notion_inbox_task
                    LOGGER.info(f"Changed inbox task with id={notion_inbox_task.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random task added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a task added by the script, but which failed before local data could be saved. We'll have
                #    duplicates in these cases, and they need to be removed.
                try:
                    self._inbox_task_notion_manager.remove_inbox_task(
                        inbox_task_collection.ref_id, notion_inbox_task.ref_id)
                    LOGGER.info(f"Removed dangling inbox task in Notion {notion_inbox_task}")
                except NotionInboxTaskNotFoundError:
                    LOGGER.info(f"Skipped dangling inbox task in Notion {notion_inbox_task}")

        LOGGER.info("Applied local changes")

        # Now, go over each local recurring task, and add it to Notion if it doesn't
        # exist there!

        for inbox_task in all_inbox_tasks_set.values():
            # We've already processed this thing above
            if inbox_task.ref_id in all_notion_inbox_tasks_set:
                continue
            if inbox_task.archived:
                continue

            direct_info = \
                NotionInboxTask.DirectInfo(
                    project_name=all_projects_map[inbox_task.project_ref_id].name,
                    big_plan_name=
                    all_big_plans_map[inbox_task.big_plan_ref_id].name if inbox_task.big_plan_ref_id else None)

            notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, direct_info)
            self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection.ref_id, notion_inbox_task)
            all_notion_inbox_tasks_set[inbox_task.ref_id] = notion_inbox_task
            LOGGER.info(f'Created Notion inbox task for {inbox_task.name}')

        return all_inbox_tasks_set.values()
