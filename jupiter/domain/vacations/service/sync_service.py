"""The service class for syncing the VACATION database between local and Notion."""
import logging
from typing import Final, Iterable, Dict, Optional

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.domain.vacations.notion_vacation import NotionVacation
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class VacationSyncService:
    """The service class for syncing the VACATION database between local and Notion."""

    _storage_engine: Final[DomainStorageEngine]
    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, vacation_notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._vacation_notion_manager = vacation_notion_manager

    def sync(
            self, workspace: Workspace, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]], sync_prefer: SyncPrefer) -> Iterable[Vacation]:
        """Synchronise vacations between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_workspace(workspace.ref_id)
            all_vacations = \
                uow.vacation_repository.find_all(
                    vacation_collection_ref_id=vacation_collection.ref_id,
                    allow_archived=True,
                    filter_ref_ids=filter_ref_ids)
        all_vacations_set: Dict[EntityId, Vacation] = {v.ref_id: v for v in all_vacations}

        if not drop_all_notion_side:
            all_notion_vacations = self._vacation_notion_manager.load_all_vacations(vacation_collection.ref_id)
            all_notion_vacations_notion_ids = \
                set(self._vacation_notion_manager.load_all_saved_vacation_notion_ids(vacation_collection.ref_id))
        else:
            self._vacation_notion_manager.drop_all_vacations(vacation_collection.ref_id)
            all_notion_vacations = []
            all_notion_vacations_notion_ids = set()
        all_notion_vacations_set: Dict[EntityId, NotionVacation] = {}

        # Explore Notion and apply to local
        for notion_vacation in all_notion_vacations:
            if filter_ref_ids_set is not None and notion_vacation.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_vacation.name}' (id={notion_vacation.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_vacation.name}' (id={notion_vacation.notion_id})")

            if notion_vacation.ref_id is None:
                new_vacation = \
                    notion_vacation.new_entity(
                        NotionVacation.InverseInfo(vacation_collection_ref_id=vacation_collection.ref_id))

                with self._storage_engine.get_unit_of_work() as uow:
                    new_vacation = uow.vacation_repository.create(new_vacation)

                self._vacation_notion_manager.link_local_and_notion_entries(
                    vacation_collection.ref_id, new_vacation.ref_id, notion_vacation.notion_id)
                LOGGER.info("Linked the new vacation with local entries")

                notion_vacation = notion_vacation.join_with_entity(new_vacation, None)
                self._vacation_notion_manager.save_vacation(vacation_collection.ref_id, notion_vacation)
                LOGGER.info(f"Applies changes on Notion side too as {notion_vacation}")

                all_vacations_set[new_vacation.ref_id] = new_vacation
                all_notion_vacations_set[new_vacation.ref_id] = notion_vacation
            elif notion_vacation.ref_id in all_vacations_set \
                    and notion_vacation.notion_id in all_notion_vacations_notion_ids:
                vacation = all_vacations_set[notion_vacation.ref_id]
                all_notion_vacations_set[notion_vacation.ref_id] = notion_vacation

                # If the vacation exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_vacation.last_edited_time <= vacation.last_modified_time:
                        LOGGER.info(f"Skipping {notion_vacation.name} because it was not modified")
                        continue

                    updated_vacation = \
                        notion_vacation.apply_to_entity(
                            vacation, NotionVacation.InverseInfo(vacation_collection_ref_id=vacation_collection.ref_id))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.vacation_repository.save(updated_vacation)

                    all_vacations_set[notion_vacation.ref_id] = updated_vacation

                    LOGGER.info(f"Changed vacation with id={notion_vacation.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified \
                            and vacation.last_modified_time <= notion_vacation.last_edited_time:
                        LOGGER.info(f"Skipping {notion_vacation.name} because it was not modified")
                        continue

                    updated_notion_vacation = notion_vacation.join_with_entity(vacation, None)

                    self._vacation_notion_manager.save_vacation(vacation_collection.ref_id, updated_notion_vacation)

                    all_notion_vacations_set[notion_vacation.ref_id] = updated_notion_vacation

                    LOGGER.info(f"Changed vacation with id={notion_vacation.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random vacation added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a vacation added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._vacation_notion_manager.remove_vacation(vacation_collection.ref_id, notion_vacation.ref_id)
                    LOGGER.info(f"Removed vacation with id={notion_vacation.ref_id} from Notion")
                except NotionVacationNotFoundError:
                    LOGGER.info(f"Skipped dangling vacation in Notion {notion_vacation.ref_id}")

        # Explore local and apply to Notion now
        for vacation in all_vacations:
            if vacation.ref_id in all_notion_vacations_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue
            if vacation.archived:
                continue

            # If the vacation does not exist on Notion side, we create it.
            notion_vacation = NotionVacation.new_notion_row(vacation, None)
            self._vacation_notion_manager.upsert_vacation(vacation_collection.ref_id, notion_vacation)
            all_notion_vacations_set[vacation.ref_id] = notion_vacation
            LOGGER.info(f"Created new vacation on Notion side {vacation.name}")

        return all_vacations_set.values()
