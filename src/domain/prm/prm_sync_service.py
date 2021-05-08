"""The service class for syncing the PRM database between local and Notion."""
import logging
from typing import Final, Iterable, Dict, Optional

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.notion_person import NotionPerson
from domain.prm.person import Person
from models.basic import BasicValidator, EntityId, SyncPrefer
from service.errors import ServiceError

LOGGER = logging.getLogger(__name__)


class PrmSyncService:
    """The service class for syncing the PRM database between local and Notion."""

    _basic_validator: Final[BasicValidator]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, basic_validator: BasicValidator, prm_engine: PrmEngine,
            prm_prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_prm_notion_manager

    def sync(
            self, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]], sync_prefer: SyncPrefer) -> Iterable[Person]:
        """Synchronise persons between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._prm_engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.load()
            all_persons = uow.person_repository.find_all(allow_archived=True, filter_ref_ids=filter_ref_ids)
        all_persons_set: Dict[EntityId, Person] = {v.ref_id: v for v in all_persons}

        if not drop_all_notion_side:
            all_persons_rows = self._prm_notion_manager.load_all_persons()
            all_persons_notion_ids = set(self._prm_notion_manager.load_all_saved_person_notion_ids())
        else:
            self._prm_notion_manager.drop_all_persons()
            all_persons_rows = []
            all_persons_notion_ids = set()
        persons_rows_set = {}

        # Explore Notion and apply to local
        for person_row in all_persons_rows:
            if filter_ref_ids_set is not None and person_row.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{person_row.name}' (id={person_row.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{person_row.name}' (id={person_row.notion_id})")

            if person_row.ref_id is None or person_row.ref_id == "":
                new_person = person_row.new_aggregate_root(prm_database.catch_up_project_ref_id)

                with self._prm_engine.get_unit_of_work() as uow:
                    new_person = uow.person_repository.create(new_person)

                self._prm_notion_manager.link_local_and_notion_entries(new_person.ref_id, person_row.notion_id)
                LOGGER.info(f"Linked the new person with local entries")

                person_row = person_row.join_with_aggregate_root(new_person)
                self._prm_notion_manager.upsert_person(person_row)
                LOGGER.info(f"Applies changes on Notion side too as {person_row}")

                persons_rows_set[person_row.ref_id] = person_row
            elif person_row.ref_id in all_persons_set and person_row.notion_id in all_persons_notion_ids:
                person = all_persons_set[EntityId(person_row.ref_id)]
                persons_rows_set[EntityId(person_row.ref_id)] = person_row

                # If the person exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and person_row.last_edited_time <= person.last_modified_time:
                        LOGGER.info(f"Skipping {person_row.name} because it was not modified")
                        continue

                    updated_person = person_row.apply_to_aggregate_root(person, prm_database.catch_up_project_ref_id)

                    with self._prm_engine.get_unit_of_work() as uow:
                        uow.person_repository.save(updated_person)
                    LOGGER.info(f"Changed person with id={person_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and person.last_modified_time <= person_row.last_edited_time:
                        LOGGER.info(f"Skipping {person_row.name} because it was not modified")
                        continue

                    updated_person_row = person_row.join_with_aggregate_root(person)

                    self._prm_notion_manager.save_person(updated_person_row)
                    LOGGER.info(f"Changed person with id={person_row.ref_id} from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random person added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a person added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._prm_notion_manager.remove_person(EntityId(person_row.ref_id))
                LOGGER.info(f"Removed person with id={person_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for person in all_persons:
            if person.ref_id in persons_rows_set:
                # The person already exists on Notion side, so it was handled by the above loop!
                continue
            if person.archived:
                continue

            # If the person does not exist on Notion side, we create it.
            notion_person = NotionPerson.new_notion_row(person)
            self._prm_notion_manager.upsert_person(notion_person)
            LOGGER.info(f"Created new person on Notion side {person.name}")

        return all_persons_set.values()
