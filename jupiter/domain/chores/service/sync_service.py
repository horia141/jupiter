"""The service class for dealing with chores."""
import logging
from typing import Final, Optional, Iterable, Dict

from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.projects.project import Project
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager, \
    NotionChoreNotFoundError
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.chores.chore import Chore
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.remote.notion.common import format_name_for_option
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ChoreSyncService:
    """The service class for dealing with chores."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _chore_notion_manager: Final[ChoreNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            chore_notion_manager: ChoreNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._chore_notion_manager = chore_notion_manager

    def chores_sync(
            self,
            workspace: Workspace,
            all_projects: Iterable[Project],
            inbox_task_collection: NotionInboxTaskCollection,
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]],
            filter_project_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[Chore]:
        """Synchronise big plans between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            chore_collection = uow.chore_collection_repository.load_by_workspace(workspace.ref_id)
            all_chores = uow.chore_repository.find_all(
                chore_collection_ref_id=chore_collection.ref_id,
                allow_archived=True, filter_ref_ids=filter_ref_ids, filter_project_ref_ids=filter_project_ref_ids)

        all_chores_set: Dict[EntityId, Chore] = {bp.ref_id: bp for bp in all_chores}

        if not drop_all_notion_side:
            all_notion_chores = \
                self._chore_notion_manager.load_all_chores(chore_collection.ref_id)
            all_notion_chores_notion_ids = \
                set(self._chore_notion_manager.load_all_saved_chores_notion_ids(
                    chore_collection.ref_id))
        else:
            self._chore_notion_manager.drop_all_chores(chore_collection.ref_id)
            all_notion_chores = {}
            all_notion_chores_notion_ids = set()
        all_notion_chores_set: Dict[EntityId, NotionChore] = {}

        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        inverse_info = \
            NotionChore.InverseInfo(
                chore_collection_ref_id=chore_collection.ref_id,
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map)

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        for notion_chore in all_notion_chores:
            # Skip this step when asking only for particular entities to be synced.
            if filter_ref_ids_set is not None and notion_chore.ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{notion_chore.name}' " +
                    f"(id={notion_chore.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_chore.name}' (id={notion_chore.notion_id})")
            if notion_chore.ref_id is None:
                # If the big plan doesn't exist locally, we create it!

                new_chore = notion_chore.new_entity(inverse_info)

                with self._storage_engine.get_unit_of_work() as save_uow:
                    new_chore = save_uow.chore_repository.create(new_chore)
                LOGGER.info(f"Found new big plan from Notion {notion_chore.name}")

                self._chore_notion_manager.link_local_and_notion_chore(
                    chore_collection.ref_id, new_chore.ref_id, notion_chore.notion_id)
                LOGGER.info("Linked the new big plan with local entries")

                direct_info = \
                    NotionChore.DirectInfo(
                        project_name=all_projects_map[new_chore.project_ref_id].name)
                notion_chore = \
                    notion_chore.join_with_entity(new_chore, direct_info)
                self._chore_notion_manager.save_chore(
                    chore_collection.ref_id, notion_chore, inbox_task_collection)
                LOGGER.info(f"Applies changes on Notion side too as {notion_chore}")

                all_chores_set[new_chore.ref_id] = new_chore
                all_notion_chores_set[new_chore.ref_id] = notion_chore
            elif notion_chore.ref_id in all_chores_set and \
                    notion_chore.notion_id in all_notion_chores_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                chore = all_chores_set[notion_chore.ref_id]
                all_notion_chores_set[notion_chore.ref_id] = notion_chore

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_chore.last_edited_time <= chore.last_modified_time:
                        LOGGER.info(f"Skipping {notion_chore.name} because it was not modified")
                        continue

                    updated_chore = \
                        notion_chore.apply_to_entity(chore, inverse_info)
                    # TODO(horia141: handle archival here! The same in all other flows! BIG ISSUE!
                    with self._storage_engine.get_unit_of_work() as save_uow:
                        save_uow.chore_repository.save(updated_chore)
                    all_chores_set[notion_chore.ref_id] = updated_chore
                    LOGGER.info(f"Changed big plan with id={notion_chore.ref_id} from Notion")

                    if notion_chore.start_at_date is None\
                            or notion_chore.project_ref_id is None\
                            or notion_chore.project_name is None:
                        direct_info = \
                            NotionChore.DirectInfo(
                                project_name=all_projects_map[chore.project_ref_id].name)
                        updated_notion_chore = \
                            notion_chore.join_with_entity(updated_chore, direct_info)
                        self._chore_notion_manager.save_chore(
                            chore_collection.ref_id, updated_notion_chore, inbox_task_collection)
                        LOGGER.info(f"Applies changes on Notion side too as {updated_notion_chore}")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            chore.last_modified_time <= notion_chore.last_edited_time:
                        LOGGER.info(f"Skipping {chore.name} because it was not modified")
                        continue

                    direct_info = \
                        NotionChore.DirectInfo(
                            project_name=all_projects_map[chore.project_ref_id].name)
                    updated_notion_chore = \
                        notion_chore.join_with_entity(chore, direct_info)
                    self._chore_notion_manager.save_chore(
                        chore_collection.ref_id, updated_notion_chore, inbox_task_collection)
                    all_notion_chores_set[notion_chore.ref_id] = updated_notion_chore
                    LOGGER.info(f"Changed big plan with id={notion_chore.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random big plan added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a big plan added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._chore_notion_manager.remove_chore(
                        chore_collection.ref_id, notion_chore.ref_id)
                    LOGGER.info(f"Removed dangling chore in Notion {notion_chore}")
                except NotionChoreNotFoundError:
                    LOGGER.info(f"Skipped dangling chore in Notion {notion_chore}")

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for chore in all_chores_set.values():
            # We've already processed this thing above
            if chore.ref_id in all_notion_chores_set:
                continue
            if chore.archived:
                continue

            direct_info = \
                NotionChore.DirectInfo(
                    project_name=all_projects_map[chore.project_ref_id].name)
            notion_chore = NotionChore.new_notion_row(chore, direct_info)
            self._chore_notion_manager.upsert_chore(
                chore_collection.ref_id, notion_chore, inbox_task_collection)
            all_notion_chores_set[chore.ref_id] = notion_chore
            LOGGER.info(f'Created Notion task for {chore.name}')

        return all_chores_set.values()
