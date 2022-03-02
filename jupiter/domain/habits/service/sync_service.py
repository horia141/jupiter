"""The service class for dealing with habits."""
import logging
from typing import Final, Optional, Iterable, Dict

from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.projects.project import Project
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager, \
    NotionHabitNotFoundError
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.habits.habit import Habit
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.remote.notion.common import format_name_for_option
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class HabitSyncService:
    """The service class for dealing with habits."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _habit_notion_manager: Final[HabitNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            habit_notion_manager: HabitNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._habit_notion_manager = habit_notion_manager

    def habits_sync(
            self,
            workspace: Workspace,
            all_projects: Iterable[Project],
            inbox_task_collection: NotionInboxTaskCollection,
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]],
            filter_project_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[Habit]:
        """Synchronise big plans between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            habit_collection = uow.habit_collection_repository.load_by_workspace(workspace.ref_id)
            all_habits = uow.habit_repository.find_all(
                habit_collection_ref_id=habit_collection.ref_id,
                allow_archived=True, filter_ref_ids=filter_ref_ids, filter_project_ref_ids=filter_project_ref_ids)

        all_habits_set: Dict[EntityId, Habit] = {bp.ref_id: bp for bp in all_habits}

        if not drop_all_notion_side:
            all_notion_habits = \
                self._habit_notion_manager.load_all_habits(habit_collection.ref_id)
            all_notion_habits_notion_ids = \
                set(self._habit_notion_manager.load_all_saved_habits_notion_ids(
                    habit_collection.ref_id))
        else:
            self._habit_notion_manager.drop_all_habits(habit_collection.ref_id)
            all_notion_habits = {}
            all_notion_habits_notion_ids = set()
        all_notion_habits_set: Dict[EntityId, NotionHabit] = {}

        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        inverse_info = \
            NotionHabit.InverseInfo(
                habit_collection_ref_id=habit_collection.ref_id,
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map)

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        for notion_habit in all_notion_habits:
            # Skip this step when asking only for particular entities to be synced.
            if filter_ref_ids_set is not None and notion_habit.ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{notion_habit.name}' " +
                    f"(id={notion_habit.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_habit.name}' (id={notion_habit.notion_id})")
            if notion_habit.ref_id is None:
                # If the big plan doesn't exist locally, we create it!

                new_habit = notion_habit.new_entity(inverse_info)

                with self._storage_engine.get_unit_of_work() as save_uow:
                    new_habit = save_uow.habit_repository.create(new_habit)
                LOGGER.info(f"Found new big plan from Notion {notion_habit.name}")

                self._habit_notion_manager.link_local_and_notion_habit(
                    habit_collection.ref_id, new_habit.ref_id, notion_habit.notion_id)
                LOGGER.info("Linked the new big plan with local entries")

                direct_info = \
                    NotionHabit.DirectInfo(
                        project_name=all_projects_map[new_habit.project_ref_id].name)
                notion_habit = \
                    notion_habit.join_with_entity(new_habit, direct_info)
                self._habit_notion_manager.save_habit(
                    habit_collection.ref_id, notion_habit, inbox_task_collection)
                LOGGER.info(f"Applies changes on Notion side too as {notion_habit}")

                all_habits_set[new_habit.ref_id] = new_habit
                all_notion_habits_set[new_habit.ref_id] = notion_habit
            elif notion_habit.ref_id in all_habits_set and \
                    notion_habit.notion_id in all_notion_habits_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                habit = all_habits_set[notion_habit.ref_id]
                all_notion_habits_set[notion_habit.ref_id] = notion_habit

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_habit.last_edited_time <= habit.last_modified_time:
                        LOGGER.info(f"Skipping {notion_habit.name} because it was not modified")
                        continue

                    updated_habit = \
                        notion_habit.apply_to_entity(habit, inverse_info)
                    # TODO(horia141: handle archival here! The same in all other flows! BIG ISSUE!
                    with self._storage_engine.get_unit_of_work() as save_uow:
                        save_uow.habit_repository.save(updated_habit)
                    all_habits_set[notion_habit.ref_id] = updated_habit
                    LOGGER.info(f"Changed big plan with id={notion_habit.ref_id} from Notion")

                    if notion_habit.project_ref_id is None\
                            or notion_habit.project_name is None:
                        direct_info = \
                            NotionHabit.DirectInfo(
                                project_name=all_projects_map[habit.project_ref_id].name)
                        updated_notion_habit = \
                            notion_habit.join_with_entity(updated_habit, direct_info)
                        self._habit_notion_manager.save_habit(
                            habit_collection.ref_id, updated_notion_habit, inbox_task_collection)
                        LOGGER.info(f"Applies changes on Notion side too as {updated_notion_habit}")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            habit.last_modified_time <= notion_habit.last_edited_time:
                        LOGGER.info(f"Skipping {habit.name} because it was not modified")
                        continue

                    direct_info = \
                        NotionHabit.DirectInfo(
                            project_name=all_projects_map[habit.project_ref_id].name)
                    updated_notion_habit = \
                        notion_habit.join_with_entity(habit, direct_info)
                    self._habit_notion_manager.save_habit(
                        habit_collection.ref_id, updated_notion_habit, inbox_task_collection)
                    all_notion_habits_set[notion_habit.ref_id] = updated_notion_habit
                    LOGGER.info(f"Changed big plan with id={notion_habit.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random big plan added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a big plan added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._habit_notion_manager.remove_habit(
                        habit_collection.ref_id, notion_habit.ref_id)
                    LOGGER.info(f"Removed dangling habit in Notion {notion_habit}")
                except NotionHabitNotFoundError:
                    LOGGER.info(f"Skipped dangling habit in Notion {notion_habit}")

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for habit in all_habits_set.values():
            # We've already processed this thing above
            if habit.ref_id in all_notion_habits_set:
                continue
            if habit.archived:
                continue

            direct_info = \
                NotionHabit.DirectInfo(
                    project_name=all_projects_map[habit.project_ref_id].name)
            notion_habit = NotionHabit.new_notion_row(habit, direct_info)
            self._habit_notion_manager.upsert_habit(
                habit_collection.ref_id, notion_habit, inbox_task_collection)
            all_notion_habits_set[habit.ref_id] = notion_habit
            LOGGER.info(f'Created Notion task for {habit.name}')

        return all_habits_set.values()
