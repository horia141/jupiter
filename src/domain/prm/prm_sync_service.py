"""The service class for syncing the PRM database between local and Notion."""
import logging
import typing
from typing import Final, Iterable, Dict, Optional

from domain.errors import ServiceError
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.notion_person import NotionPerson
from domain.prm.person import Person
from domain.sync_prefer import SyncPrefer
from framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class PrmSyncService:
    """The service class for syncing the PRM database between local and Notion."""

    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, prm_engine: PrmEngine, prm_prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
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
            all_notion_persons = self._prm_notion_manager.load_all_persons()
            all_notion_persons_notion_ids = set(self._prm_notion_manager.load_all_saved_person_notion_ids())
        else:
            self._prm_notion_manager.drop_all_persons()
            all_notion_persons = []
            all_notion_persons_notion_ids = set()
        all_notion_persons_set: Dict[EntityId, NotionPerson] = {}

        # Explore Notion and apply to local
        for notion_person in all_notion_persons:
            notion_person_ref_id = EntityId.from_raw(notion_person.ref_id) if notion_person.ref_id else None
            if filter_ref_ids_set is not None and notion_person_ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_person.name}' (id={notion_person.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{notion_person.name}' (id={notion_person.notion_id})")

            if notion_person.ref_id is None or notion_person.ref_id == "":
                new_person = \
                    notion_person.new_aggregate_root(
                        NotionPerson.InverseExtraInfo(prm_database.catch_up_project_ref_id))

                with self._prm_engine.get_unit_of_work() as uow:
                    new_person = uow.person_repository.create(new_person)

                self._prm_notion_manager.link_local_and_notion_entries(new_person.ref_id, notion_person.notion_id)
                LOGGER.info(f"Linked the new person with local entries")

                notion_person = notion_person.join_with_aggregate_root(new_person, None)
                self._prm_notion_manager.save_person(notion_person)
                LOGGER.info(f"Applies changes on Notion side too as {notion_person}")

                all_notion_persons_set[new_person.ref_id] = notion_person
            elif notion_person_ref_id in all_persons_set and notion_person.notion_id in all_notion_persons_notion_ids:
                person = all_persons_set[notion_person_ref_id]
                all_notion_persons_set[notion_person_ref_id] = notion_person

                # If the person exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and notion_person.last_edited_time <= person.last_modified_time:
                        LOGGER.info(f"Skipping {notion_person.name} because it was not modified")
                        continue

                    updated_person = \
                        notion_person.apply_to_aggregate_root(
                            person, NotionPerson.InverseExtraInfo(prm_database.catch_up_project_ref_id))

                    with self._prm_engine.get_unit_of_work() as uow:
                        uow.person_repository.save(updated_person)
                    LOGGER.info(f"Changed person with id={notion_person.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and person.last_modified_time <= notion_person.last_edited_time:
                        LOGGER.info(f"Skipping {notion_person.name} because it was not modified")
                        continue

                    updated_notion_person = notion_person.join_with_aggregate_root(person, None)

                    self._prm_notion_manager.save_person(updated_notion_person)
                    LOGGER.info(f"Changed person with id={notion_person.ref_id} from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random person added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a person added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._prm_notion_manager.remove_person(typing.cast(EntityId, notion_person_ref_id))
                LOGGER.info(f"Removed person with id={notion_person.ref_id} from Notion")

        # Explore local and apply to Notion now
        for person in all_persons:
            if person.ref_id in all_notion_persons_set:
                # The person already exists on Notion side, so it was handled by the above loop!
                continue
            if person.archived:
                continue

            # If the person does not exist on Notion side, we create it.
            notion_person = NotionPerson.new_notion_row(person, None)
            self._prm_notion_manager.upsert_person(notion_person)
            LOGGER.info(f"Created new person on Notion side {person.name}")

        return all_persons_set.values()
