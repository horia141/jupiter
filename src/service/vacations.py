"""The service class for dealing with vacations."""
import logging
from typing import Final, Iterable, Dict

import pendulum

from models.basic import BasicValidator, EntityId, SyncPrefer, ModelValidationError
from remote.notion.common import NotionPageLink, NotionCollectionLink
from remote.notion.vacations import VacationsCollection
from repository.vacations import VacationsRepository, Vacation
from service.errors import ServiceError, ServiceValidationError

LOGGER = logging.getLogger(__name__)


class VacationsService:
    """The service class for dealing with vacations."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[VacationsRepository]
    _collection: Final[VacationsCollection]

    def __init__(
            self, basic_validator: BasicValidator, repository: VacationsRepository,
            collection: VacationsCollection) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._collection = collection

    def upsert_notion_structure(self, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Upsert the Notion-side structure for vacations."""
        return self._collection.upsert_vacations_structure(parent_page)

    def create_vacation(self, name: str, start_date: pendulum.DateTime, end_date: pendulum.DateTime) -> Vacation:
        """Create a vacation."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)

            if start_date >= end_date:
                raise ServiceValidationError(f"Start date {start_date} is after {end_date}")
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally

        new_vacation = self._repository.create_vacation(
            archived=False,
            name=name,
            start_date=start_date,
            end_date=end_date)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        self._collection.create_vacation(
            archived=False,
            name=name,
            start_date=start_date,
            end_date=end_date,
            ref_id=new_vacation.ref_id)
        LOGGER.info("Applied Notion changes")

        return new_vacation

    def archive_vacation(self, ref_id: EntityId) -> Vacation:
        """Archive a given vacation."""
        # Apply changes locally

        vacation = self._repository.archive_vacation(ref_id)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        self._collection.archive_vacation(ref_id)
        LOGGER.info("Applied Notion changes")

        return vacation

    def set_vacation_name(self, ref_id: EntityId, name: str) -> Vacation:
        """Change the name of a vacation."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally

        vacation = self._repository.load_vacation(ref_id)
        vacation.name = name
        self._repository.save_vacation(vacation)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacation_row = self._collection.load_vacation(vacation.ref_id)
        vacation_row.name = name
        self._collection.save_vacation(vacation_row)
        LOGGER.info("Applied Notion changes")

        return vacation

    def set_vacation_start_date(self, ref_id: EntityId, start_date: pendulum.DateTime) -> Vacation:
        """Change the start date of a vacation."""
        # Apply changes locally

        vacation = self._repository.load_vacation(ref_id)
        if start_date >= vacation.end_date:
            raise ServiceValidationError("Cannot set a start date after the end date")
        vacation.start_date = start_date
        self._repository.save_vacation(vacation)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacation_row = self._collection.load_vacation(vacation.ref_id)
        vacation_row.start_date = start_date
        self._collection.save_vacation(vacation_row)
        LOGGER.info("Applied Notion changes")

        return vacation

    def set_vacation_end_date(self, ref_id: EntityId, end_date: pendulum.DateTime) -> Vacation:
        """Change the end date of a vacation."""
        # Apply changes locally

        vacation = self._repository.load_vacation(ref_id)
        if end_date <= vacation.start_date:
            raise ServiceValidationError("Cannot set an end date before the start date")
        vacation.end_date = end_date
        self._repository.save_vacation(vacation)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacation_row = self._collection.load_vacation(vacation.ref_id)
        vacation_row.end_date = end_date
        self._collection.save_vacation(vacation_row)
        LOGGER.info("Applied Notion changes")

        return vacation

    def hard_remove_vacation(self, ref_id: EntityId) -> Vacation:
        """Hard remove an big plan."""
        # Apply changes locally
        vacation = self._repository.hard_remove_vacation(ref_id)
        LOGGER.info("Applied local changes")
        vacation_row = self._collection.load_vacation(ref_id)
        self._collection.hard_remove_vacation(vacation_row)
        LOGGER.info("Applied Notion changes")

        return vacation

    def load_all_vacations(self, show_archived: bool = False) -> Iterable[Vacation]:
        """Retrieve all vacations."""
        return self._repository.load_all_vacations(filter_archived=not show_archived)

    def vacations_sync(self, drop_all_notion_side: bool, sync_prefer: SyncPrefer) -> None:
        """Synchronise vacations between Notion and local storage."""
        all_vacations = self._repository.load_all_vacations(filter_archived=False)
        all_vacations_set: Dict[EntityId, Vacation] = {v.ref_id: v for v in all_vacations}

        if not drop_all_notion_side:
            all_vacations_rows = self._collection.load_all_vacations()
            all_vacations_notion_ids = set(self._collection.load_all_saved_vacation_notion_ids())
        else:
            self._collection.drop_all_vacations()
            all_vacations_rows = {}
            all_vacations_notion_ids = set()
        vacations_rows_set = {}

        # Explore Notion and apply to local
        for vacation_row in all_vacations_rows:
            LOGGER.info(f"Processing {vacation_row.name}")
            if vacation_row.ref_id is None or vacation_row.ref_id == "":
                # If the vacation doesn't exist locally, we create it:
                try:
                    vacation_name = self._basic_validator.entity_name_validate_and_clean(vacation_row.name)
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                if not vacation_row.start_date:
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have a start date")
                if not vacation_row.end_date:
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have an end date")
                if vacation_row.start_date >= vacation_row.end_date:
                    raise ServiceValidationError(
                        f"Start date for vacation {vacation_row.name} is after end date")

                new_vacation = self._repository.create_vacation(
                    archived=False,
                    name=vacation_name,
                    start_date=pendulum.instance(vacation_row.start_date),
                    end_date=pendulum.instance(vacation_row.end_date))
                LOGGER.info(f"Found new vacation from Notion {vacation_row.name}")

                self._collection.link_local_and_notion_entries(new_vacation.ref_id, vacation_row.notion_id)
                LOGGER.info(f"Linked the new vacation with local entries")

                vacation_row.ref_id = new_vacation.ref_id
                self._collection.save_vacation(vacation_row)
                LOGGER.info(f"Applies changes on Notion side too as {vacation_row}")

                vacations_rows_set[vacation_row.ref_id] = vacation_row
            elif vacation_row.ref_id in all_vacations_set and vacation_row.notion_id in all_vacations_notion_ids:
                vacation = all_vacations_set[EntityId(vacation_row.ref_id)]
                # If the vacation exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    try:
                        vacation_name = self._basic_validator.entity_name_validate_and_clean(vacation_row.name)
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    if not vacation_row.start_date:
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have a start date")
                    if not vacation_row.end_date:
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have an end date")
                    if vacation_row.start_date >= vacation_row.end_date:
                        raise ServiceValidationError(
                            f"Start date for vacation {vacation_row.name} is after end date")

                    vacation.archived = vacation_row.archived
                    vacation.name = vacation_name
                    vacation.start_date = vacation_row.start_date
                    vacation.end_date = vacation_row.end_date
                    self._repository.save_vacation(vacation)
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    vacation_row.archived = vacation.archived
                    vacation_row.name = vacation.name
                    vacation_row.start_date = vacation.start_date
                    vacation_row.end_date = vacation.end_date
                    self._collection.save_vacation(vacation_row)
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
                vacations_rows_set[EntityId(vacation_row.ref_id)] = vacation_row
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random vacation added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a vacation added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._collection.hard_remove_vacation(vacation_row)
                LOGGER.info(f"Removed vacation with id={vacation_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for vacation in all_vacations:
            if vacation.ref_id in vacations_rows_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue

            # If the vacation does not exist on Notion side, we create it.
            new_vacation_row = self._collection.create_vacation(
                archived=vacation.archived,
                name=vacation.name,
                start_date=vacation.start_date,
                end_date=vacation.end_date,
                ref_id=vacation.ref_id)
            LOGGER.info(f"Created new vacation on Notion side {new_vacation_row}")
