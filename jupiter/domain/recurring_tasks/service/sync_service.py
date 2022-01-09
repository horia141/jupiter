"""The service class for dealing with recurring tasks."""
import logging
from typing import Final, Optional, Iterable, Dict

from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager, \
    NotionRecurringTaskNotFoundError
from jupiter.domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.framework.base.entity_id import EntityId
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskSyncService:
    """The service class for dealing with recurring tasks."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def recurring_tasks_sync(
            self, project_ref_id: EntityId, drop_all_notion_side: bool,
            inbox_task_collection: NotionInboxTaskCollection, sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]], sync_prefer: SyncPrefer) -> Iterable[RecurringTask]:
        """Synchronise big plans between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task_collection = uow.recurring_task_collection_repository.load_by_project(project_ref_id)
            all_recurring_tasks = uow.recurring_task_repository.find_all(
                allow_archived=True, filter_ref_ids=filter_ref_ids,
                filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id])

        all_recurring_tasks_set: Dict[EntityId, RecurringTask] = {bp.ref_id: bp for bp in all_recurring_tasks}

        if not drop_all_notion_side:
            all_notion_recurring_tasks = \
                self._recurring_task_notion_manager.load_all_recurring_tasks(recurring_task_collection.ref_id)
            all_notion_recurring_tasks_notion_ids = \
                set(self._recurring_task_notion_manager.load_all_saved_recurring_tasks_notion_ids(
                    recurring_task_collection.ref_id))
        else:
            self._recurring_task_notion_manager.drop_all_recurring_tasks(recurring_task_collection.ref_id)
            all_notion_recurring_tasks = {}
            all_notion_recurring_tasks_notion_ids = set()
        all_notion_recurring_tasks_set: Dict[EntityId, NotionRecurringTask] = {}

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        for notion_recurring_task in all_notion_recurring_tasks:
            # Skip this step when asking only for particular entities to be synced.
            notion_recurring_task_ref_id = \
                EntityId.from_raw(notion_recurring_task.ref_id) if notion_recurring_task.ref_id else None
            if filter_ref_ids_set is not None and notion_recurring_task_ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{notion_recurring_task.name}' " +
                    f"(id={notion_recurring_task.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_recurring_task.name}' (id={notion_recurring_task.notion_id})")
            if notion_recurring_task_ref_id is None or notion_recurring_task.ref_id == "":
                # If the big plan doesn't exist locally, we create it!

                new_recurring_task = \
                    notion_recurring_task.new_aggregate_root(
                        NotionRecurringTask.InverseExtraInfo(project_ref_id, recurring_task_collection.ref_id))

                with self._storage_engine.get_unit_of_work() as save_uow:
                    new_recurring_task = \
                        save_uow.recurring_task_repository.create(recurring_task_collection, new_recurring_task)
                LOGGER.info(f"Found new big plan from Notion {notion_recurring_task.name}")

                self._recurring_task_notion_manager.link_local_and_notion_recurring_task(
                    recurring_task_collection.ref_id, new_recurring_task.ref_id, notion_recurring_task.notion_id)
                LOGGER.info(f"Linked the new big plan with local entries")

                notion_recurring_task = notion_recurring_task.join_with_aggregate_root(new_recurring_task, None)
                self._recurring_task_notion_manager.save_recurring_task(
                    recurring_task_collection.ref_id, notion_recurring_task, inbox_task_collection)
                LOGGER.info(f"Applies changes on Notion side too as {notion_recurring_task}")

                all_recurring_tasks_set[new_recurring_task.ref_id] = new_recurring_task
                all_notion_recurring_tasks_set[new_recurring_task.ref_id] = notion_recurring_task
            elif notion_recurring_task_ref_id in all_recurring_tasks_set and \
                    notion_recurring_task.notion_id in all_notion_recurring_tasks_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                recurring_task = all_recurring_tasks_set[notion_recurring_task_ref_id]
                all_notion_recurring_tasks_set[notion_recurring_task_ref_id] = notion_recurring_task

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_recurring_task.last_edited_time <= recurring_task.last_modified_time:
                        LOGGER.info(f"Skipping {notion_recurring_task.name} because it was not modified")
                        continue

                    updated_recurring_task = \
                        notion_recurring_task.apply_to_aggregate_root(
                            recurring_task,
                            NotionRecurringTask.InverseExtraInfo(project_ref_id, recurring_task_collection.ref_id))
                    # TODO(horia141: handle archival here! The same in all other flows! BIG ISSUE!
                    with self._storage_engine.get_unit_of_work() as save_uow:
                        save_uow.recurring_task_repository.save(updated_recurring_task)
                    all_recurring_tasks_set[notion_recurring_task_ref_id] = updated_recurring_task
                    LOGGER.info(f"Changed big plan with id={notion_recurring_task.ref_id} from Notion")

                    if notion_recurring_task.the_type is None or notion_recurring_task.start_at_date is None:
                        updated_notion_recurring_task = \
                            notion_recurring_task.join_with_aggregate_root(updated_recurring_task, None)
                        self._recurring_task_notion_manager.save_recurring_task(
                            recurring_task_collection.ref_id, updated_notion_recurring_task, inbox_task_collection)
                        LOGGER.info(f"Applies changes on Notion side too as {notion_recurring_task}")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            recurring_task.last_modified_time <= notion_recurring_task.last_edited_time:
                        LOGGER.info(f"Skipping {recurring_task.name} because it was not modified")
                        continue

                    updated_notion_recurring_task = notion_recurring_task.join_with_aggregate_root(recurring_task, None)
                    self._recurring_task_notion_manager.save_recurring_task(
                        recurring_task_collection.ref_id, updated_notion_recurring_task, inbox_task_collection)
                    all_notion_recurring_tasks_set[notion_recurring_task_ref_id] = updated_notion_recurring_task
                    LOGGER.info(f"Changed big plan with id={notion_recurring_task.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random big plan added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a big plan added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._recurring_task_notion_manager.remove_recurring_task(
                        recurring_task_collection.ref_id, notion_recurring_task_ref_id)
                    LOGGER.info(f"Removed dangling recurring task in Notion {notion_recurring_task}")
                except NotionRecurringTaskNotFoundError:
                    LOGGER.info(f"Skipped dangling recurring task in Notion {notion_recurring_task}")

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for recurring_task in all_recurring_tasks_set.values():
            # We've already processed this thing above
            if recurring_task.ref_id in all_notion_recurring_tasks_set:
                continue
            if recurring_task.archived:
                continue

            notion_recurring_task = NotionRecurringTask.new_notion_row(recurring_task, None)
            self._recurring_task_notion_manager.upsert_recurring_task(
                recurring_task_collection.ref_id, notion_recurring_task, inbox_task_collection)
            all_notion_recurring_tasks_set[recurring_task.ref_id] = notion_recurring_task
            LOGGER.info(f'Created Notion task for {recurring_task.name}')

        return all_recurring_tasks_set.values()
