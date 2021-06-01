"""The service class for dealing with vacations."""
import logging
from typing import Final, Iterable, Dict, Optional

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.vacation import Vacation
from models.basic import BasicValidator, SyncPrefer
from models.framework import EntityId
from models.errors import ModelValidationError
from remote.notion.common import NotionPageLink
from remote.notion.vacations_manager import NotionVacationsManager
from service.errors import ServiceError, ServiceValidationError
from utils.storage import StructuredStorageError

LOGGER = logging.getLogger(__name__)


class VacationsService:
    """The service class for dealing with vacations."""

    _basic_validator: Final[BasicValidator]
    _vacation_engine: Final[VacationEngine]
    _notion_manager: Final[NotionVacationsManager]

    def __init__(
            self, basic_validator: BasicValidator, vacation_engine: VacationEngine,
            notion_manager: NotionVacationsManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._vacation_engine = vacation_engine
        self._notion_manager = notion_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Upsert the Notion-side structure for vacations."""
        self._notion_manager.upsert_root_page(parent_page)

    def load_all_vacations(self, allow_archived: bool = False) -> Iterable[Vacation]:
        """Retrieve all vacations."""
        with self._vacation_engine.get_unit_of_work() as uow:
            return uow.vacation_repository.find_all(allow_archived=allow_archived)

    def load_all_vacations_not_notion_gced(self) -> Iterable[Vacation]:
        """Retrieve all vacation which haven't been gced on Notion side."""
        allowed_ref_ids = self._notion_manager.load_all_saved_vacation_ref_ids()

        with self._vacation_engine.get_unit_of_work() as uow:
            return uow.vacation_repository.find_all(allow_archived=True, filter_ref_ids=allowed_ref_ids)

    def hard_remove_vacation(self, ref_id: EntityId) -> None:
        """Hard remove an big plan."""
        # Apply changes locally
        with self._vacation_engine.get_unit_of_work() as uow:
            uow.vacation_repository.remove(ref_id)
            LOGGER.info("Applied local changes")

        try:
            self._notion_manager.remove_vacation(ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping removal on Notion side because vacation was not found")

    def remove_vacation_on_notion_side(self, ref_id: EntityId) -> None:
        """Remove entries for a vacation on Notion-side."""
        try:
            self._notion_manager.remove_vacation(ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping removal on Notion side because vacation was not found")

    def vacations_sync(
            self, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]], sync_prefer: SyncPrefer) -> Iterable[Vacation]:
        """Synchronise vacations between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._vacation_engine.get_unit_of_work() as uow:
            all_vacations = uow.vacation_repository.find_all(allow_archived=True, filter_ref_ids=filter_ref_ids)
        all_vacations_set: Dict[EntityId, Vacation] = {v.ref_id: v for v in all_vacations}

        if not drop_all_notion_side:
            all_vacations_rows = self._notion_manager.load_all_vacations()
            all_vacations_notion_ids = set(self._notion_manager.load_all_saved_vacation_notion_ids())
        else:
            self._notion_manager.drop_all_vacations()
            all_vacations_rows = []
            all_vacations_notion_ids = set()
        vacations_rows_set = {}

        # Explore Notion and apply to local
        for vacation_row in all_vacations_rows:
            notion_vacation_ref_id = EntityId.from_raw(vacation_row.ref_id) if vacation_row.ref_id else None
            if filter_ref_ids_set is not None and notion_vacation_ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{vacation_row.name}' (id={vacation_row.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{vacation_row.name}' (id={vacation_row.notion_id})")

            if notion_vacation_ref_id is None or vacation_row.ref_id == "":
                # If the vacation doesn't exist locally, we create it:
                try:
                    vacation_name = self._basic_validator.entity_name_validate_and_clean(vacation_row.name)
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                if not vacation_row.start_date:
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have a start date")
                if not vacation_row.end_date:
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have an end date")
                new_vacation = Vacation.new_vacation(
                    archived=vacation_row.archived,
                    name=vacation_name,
                    start_date=vacation_row.start_date,
                    end_date=vacation_row.end_date,
                    created_time=vacation_row.last_edited_time)
                with self._vacation_engine.get_unit_of_work() as uow:
                    new_vacation = uow.vacation_repository.create(new_vacation)

                self._notion_manager.link_local_and_notion_entries(new_vacation.ref_id, vacation_row.notion_id)
                LOGGER.info(f"Linked the new vacation with local entries")

                vacation_row.ref_id = str(new_vacation.ref_id)
                self._notion_manager.save_vacation(new_vacation.ref_id, vacation_row)
                LOGGER.info(f"Applies changes on Notion side too as {vacation_row}")

                vacations_rows_set[new_vacation.ref_id] = vacation_row
            elif notion_vacation_ref_id in all_vacations_set and vacation_row.notion_id in all_vacations_notion_ids:
                vacation = all_vacations_set[notion_vacation_ref_id]
                vacations_rows_set[notion_vacation_ref_id] = vacation_row

                # If the vacation exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and vacation_row.last_edited_time <= vacation.last_modified_time:
                        LOGGER.info(f"Skipping {vacation_row.name} because it was not modified")
                        continue

                    try:
                        vacation_name = self._basic_validator.entity_name_validate_and_clean(vacation_row.name)
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    if not vacation_row.start_date:
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have a start date")
                    if not vacation_row.end_date:
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have an end date")

                    vacation.change_name(vacation_name, vacation_row.last_edited_time)
                    vacation.change_start_date(vacation_row.start_date, vacation_row.last_edited_time)
                    vacation.change_end_date(vacation_row.end_date, vacation_row.last_edited_time)
                    vacation.change_archived(vacation_row.archived, vacation_row.last_edited_time)
                    with self._vacation_engine.get_unit_of_work() as uow:
                        uow.vacation_repository.save(vacation)
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and vacation.last_modified_time <= vacation_row.last_edited_time:
                        LOGGER.info(f"Skipping {vacation_row.name} because it was not modified")
                        continue

                    vacation_row.archived = vacation.archived
                    vacation_row.name = vacation.name
                    vacation_row.start_date = vacation.start_date
                    vacation_row.end_date = vacation.end_date
                    self._notion_manager.save_vacation(vacation.ref_id, vacation_row)
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random vacation added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a vacation added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.remove_vacation(notion_vacation_ref_id)
                LOGGER.info(f"Removed vacation with id={vacation_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for vacation in all_vacations:
            if vacation.ref_id in vacations_rows_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue
            if vacation.archived:
                continue

            # If the vacation does not exist on Notion side, we create it.
            self._notion_manager.upsert_vacation(vacation)
            LOGGER.info(f"Created new vacation on Notion side {vacation.name}")

        return all_vacations_set.values()
