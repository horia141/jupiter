"""The service class for dealing with big plans."""
import logging
from typing import Final, Optional, Iterable, Dict

from domain.big_plans.big_plan import BigPlan
from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from domain.big_plans.notion_big_plan import NotionBigPlan
from domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from domain.sync_prefer import SyncPrefer
from framework.base.entity_id import EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanSyncService:
    """The service class for dealing with big plans."""

    _time_provider: Final[TimeProvider]
    _engine: Final[BigPlanEngine]
    _notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider, engine: BigPlanEngine, notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._engine = engine
        self._notion_manager = notion_manager

    def big_plans_sync(
            self, project_ref_id: EntityId, drop_all_notion_side: bool,
            inbox_task_collection: NotionInboxTaskCollection, sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]], sync_prefer: SyncPrefer) -> Iterable[BigPlan]:
        """Synchronise big plans between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._engine.get_unit_of_work() as uow:
            big_plan_collection = uow.big_plan_collection_repository.load_by_project(project_ref_id)
            all_big_plans = uow.big_plan_repository.find_all(
                allow_archived=True, filter_ref_ids=filter_ref_ids,
                filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])

        all_big_plans_set: Dict[EntityId, BigPlan] = {bp.ref_id: bp for bp in all_big_plans}

        if not drop_all_notion_side:
            all_notion_big_plans = self._notion_manager.load_all_big_plans(big_plan_collection)
            all_notion_big_plans_notion_ids = \
                set(self._notion_manager.load_all_saved_big_plans_notion_ids(project_ref_id))
        else:
            self._notion_manager.drop_all_big_plans(project_ref_id)
            all_notion_big_plans = {}
            all_notion_big_plans_notion_ids = set()
        all_notion_big_plans_set: Dict[EntityId, NotionBigPlan] = {}

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        for notion_big_plan in all_notion_big_plans:
            # Skip this step when asking only for particular entities to be synced.
            notion_big_plan_ref_id = \
                EntityId.from_raw(notion_big_plan.ref_id) if notion_big_plan.ref_id else None
            if filter_ref_ids_set is not None and notion_big_plan_ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{notion_big_plan.name}' (id={notion_big_plan.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_big_plan.name}' (id={notion_big_plan.notion_id})")
            if notion_big_plan_ref_id is None or notion_big_plan.ref_id == "":
                # If the big plan doesn't exist locally, we create it!

                new_big_plan = \
                    notion_big_plan.new_aggregate_root(NotionBigPlan.InverseExtraInfo(big_plan_collection.ref_id))

                with self._engine.get_unit_of_work() as save_uow:
                    new_big_plan = save_uow.big_plan_repository.create(big_plan_collection, new_big_plan)
                LOGGER.info(f"Found new big plan from Notion {notion_big_plan.name}")

                self._notion_manager.link_local_and_notion_big_plan(
                    project_ref_id, new_big_plan.ref_id, notion_big_plan.notion_id)
                LOGGER.info(f"Linked the new big plan with local entries")

                notion_big_plan = notion_big_plan.join_with_aggregate_root(new_big_plan, None)
                self._notion_manager.save_big_plan(project_ref_id, notion_big_plan, inbox_task_collection)
                LOGGER.info(f"Applies changes on Notion side too as {notion_big_plan}")

                all_big_plans_set[new_big_plan.ref_id] = new_big_plan
                all_notion_big_plans_set[new_big_plan.ref_id] = notion_big_plan
            elif notion_big_plan_ref_id in all_big_plans_set and \
                    notion_big_plan.notion_id in all_notion_big_plans_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                big_plan = all_big_plans_set[notion_big_plan_ref_id]
                all_notion_big_plans_set[notion_big_plan_ref_id] = notion_big_plan

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_big_plan.last_edited_time <= big_plan.last_modified_time:
                        LOGGER.info(f"Skipping {notion_big_plan.name} because it was not modified")
                        continue

                    updated_big_plan = \
                        notion_big_plan.apply_to_aggregate_root(
                            big_plan, NotionBigPlan.InverseExtraInfo(big_plan_collection.ref_id))
                    with self._engine.get_unit_of_work() as save_uow:
                        save_uow.big_plan_repository.save(updated_big_plan)
                    LOGGER.info(f"Changed big plan with id={notion_big_plan.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            big_plan.last_modified_time <= notion_big_plan.last_edited_time:
                        LOGGER.info(f"Skipping {big_plan.name} because it was not modified")
                        continue

                    updated_notion_big_plan = notion_big_plan.join_with_aggregate_root(big_plan, None)
                    self._notion_manager.save_big_plan(project_ref_id, updated_notion_big_plan, inbox_task_collection)
                    LOGGER.info(f"Changed big plan with id={notion_big_plan.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random big plan added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a big plan added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_big_plan(project_ref_id, notion_big_plan_ref_id)
                LOGGER.info(f"Removed dangling big plan in Notion {notion_big_plan}")

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for big_plan in all_big_plans_set.values():
            # We've already processed this thing above
            if big_plan.ref_id in all_notion_big_plans_set:
                continue
            if big_plan.archived:
                continue

            notion_big_plan = NotionBigPlan.new_notion_row(big_plan, None)
            self._notion_manager.upsert_big_plan(big_plan_collection, notion_big_plan, inbox_task_collection)
            LOGGER.info(f'Created Notion task for {big_plan.name}')

        return all_big_plans_set.values()
