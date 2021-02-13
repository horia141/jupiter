"""The service class for dealing with vacations."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Dict, Optional
import typing

import pendulum
from pendulum import UTC

from models.basic import BasicValidator, EntityId, SyncPrefer, ModelValidationError, ADate
from remote.notion.common import NotionPageLink, CollectionEntityNotFound
from remote.notion.vacations_manager import NotionVacationsManager
from repository.vacations import VacationsRepository, VacationRow
from service.errors import ServiceError, ServiceValidationError
from utils.storage import StructuredStorageError
from utils.time_field_action import TimeFieldAction

LOGGER = logging.getLogger(__name__)


@dataclass()
class Vacation:
    """A vacation."""

    ref_id: EntityId
    name: str
    start_date: pendulum.Date
    end_date: pendulum.Date
    archived: bool

    def is_in_vacation(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this vacation."""
        if isinstance(start_date, pendulum.DateTime):
            vacation_start_date = pendulum.DateTime(
                self.start_date.year, self.start_date.month, self.start_date.day, tzinfo=UTC)
        else:
            vacation_start_date = self.start_date
        if isinstance(end_date, pendulum.DateTime):
            vacation_end_date = pendulum.DateTime(
                self.end_date.year, self.end_date.month, self.end_date.day, tzinfo=UTC).end_of("day")
        else:
            vacation_end_date = self.end_date
        return typing.cast(bool, vacation_start_date <= start_date) and \
               typing.cast(bool, end_date <= vacation_end_date)


class VacationsService:
    """The service class for dealing with vacations."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[VacationsRepository]
    _notion_manager: Final[NotionVacationsManager]

    def __init__(
            self, basic_validator: BasicValidator, repository: VacationsRepository,
            notion_manager: NotionVacationsManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._notion_manager = notion_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Upsert the Notion-side structure for vacations."""
        self._notion_manager.upsert_root_page(parent_page)

    def create_vacation(self, name: str, start_date: ADate, end_date: ADate) -> Vacation:
        """Create a vacation."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)

            if start_date >= end_date:
                raise ServiceValidationError(f"Start date {start_date} is after {end_date}")
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally

        new_vacation_row = self._repository.create_vacation(
            archived=False,
            name=name,
            start_date=start_date,
            end_date=end_date)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        self._notion_manager.upsert_vacation(
            archived=False,
            name=name,
            start_date=start_date,
            end_date=end_date,
            ref_id=new_vacation_row.ref_id)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(new_vacation_row)

    def archive_vacation(self, ref_id: EntityId) -> Vacation:
        """Archive a given vacation."""
        # Apply changes locally

        vacation_row = self._repository.archive_vacation(ref_id)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        try:
            self._notion_manager.archive_vacation(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because vacation was not found")

        return self._row_to_entity(vacation_row)

    def set_vacation_name(self, ref_id: EntityId, name: str) -> Vacation:
        """Change the name of a vacation."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally

        vacation_row = self._repository.load_vacation(ref_id)
        vacation_row.name = name
        self._repository.update_vacation(vacation_row)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacation_notion_row = self._notion_manager.load_vacation(vacation_row.ref_id)
        vacation_notion_row.name = name
        self._notion_manager.save_vacation(ref_id, vacation_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(vacation_row)

    def set_vacation_start_date(self, ref_id: EntityId, start_date: ADate) -> Vacation:
        """Change the start date of a vacation."""
        # Apply changes locally
        if isinstance(start_date, pendulum.DateTime):
            raise ServiceValidationError("Vacations can only start on a day")

        vacation_row = self._repository.load_vacation(ref_id)
        if start_date >= vacation_row.end_date:
            raise ServiceValidationError("Cannot set a start date after the end date")
        vacation_row.start_date = start_date
        self._repository.update_vacation(vacation_row)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacation_notion_row = self._notion_manager.load_vacation(vacation_row.ref_id)
        vacation_notion_row.start_date = start_date
        self._notion_manager.save_vacation(ref_id, vacation_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(vacation_row)

    def set_vacation_end_date(self, ref_id: EntityId, end_date: ADate) -> Vacation:
        """Change the end date of a vacation."""
        # Apply changes locally
        if isinstance(end_date, pendulum.DateTime):
            raise ServiceValidationError("Vacations can only end on a day")

        vacation_row = self._repository.load_vacation(ref_id)
        if end_date <= vacation_row.start_date:
            raise ServiceValidationError("Cannot set an end date before the start date")
        vacation_row.end_date = end_date
        self._repository.update_vacation(vacation_row)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacation_notion_row = self._notion_manager.load_vacation(vacation_row.ref_id)
        vacation_notion_row.end_date = end_date
        self._notion_manager.save_vacation(ref_id, vacation_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(vacation_row)

    def load_all_vacations(self, allow_archived: bool = False) -> Iterable[Vacation]:
        """Retrieve all vacations."""
        return [self._row_to_entity(v)
                for v in self._repository.load_all_vacations(allow_archived=allow_archived)]

    def load_all_vacations_not_notion_gced(self) -> Iterable[Vacation]:
        """Retrieve all vacation which haven't been gced on Notion side."""
        allowed_ref_ids = self._notion_manager.load_all_saved_vacation_ref_ids()

        return [self._row_to_entity(v)
                for v in self._repository.load_all_vacations(allow_archived=True)
                if v.ref_id in allowed_ref_ids]

    def hard_remove_vacation(self, ref_id: EntityId) -> Vacation:
        """Hard remove an big plan."""
        # Apply changes locally
        vacation_row = self._repository.remove_vacation(ref_id)
        LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_vacation(ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping removal on Notion side because vacation was not found")

        return self._row_to_entity(vacation_row)

    def remove_vacation_on_notion_side(self, ref_id: EntityId) -> Vacation:
        """Remove entries for a vacation on Notion-side."""
        vacation_row = self._repository.load_vacation(ref_id, allow_archived=True)
        try:
            self._notion_manager.hard_remove_vacation(ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping removal on Notion side because vacation was not found")

        return self._row_to_entity(vacation_row)

    def vacations_sync(
            self, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]], sync_prefer: SyncPrefer) -> Iterable[Vacation]:
        """Synchronise vacations between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        all_vacations = self._repository.load_all_vacations(allow_archived=True, filter_ref_ids=filter_ref_ids)
        all_vacations_set: Dict[EntityId, VacationRow] = {v.ref_id: v for v in all_vacations}

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
            if filter_ref_ids_set is not None and vacation_row.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{vacation_row.name}' (id={vacation_row.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{vacation_row.name}' (id={vacation_row.notion_id})")

            if vacation_row.ref_id is None or vacation_row.ref_id == "":
                # If the vacation doesn't exist locally, we create it:
                try:
                    vacation_name = self._basic_validator.entity_name_validate_and_clean(vacation_row.name)
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                if not vacation_row.start_date:
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have a start date")
                if isinstance(vacation_row.start_date, pendulum.DateTime):
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should just start on a day")
                if not vacation_row.end_date:
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have an end date")
                if isinstance(vacation_row.end_date, pendulum.DateTime):
                    raise ServiceValidationError(f"Vacation '{vacation_row.name}' should just end on a day")
                if vacation_row.start_date >= vacation_row.end_date:
                    raise ServiceValidationError(
                        f"Start date for vacation {vacation_row.name} is after end date")

                new_vacation = self._repository.create_vacation(
                    archived=vacation_row.archived,
                    name=vacation_name,
                    start_date=vacation_row.start_date,
                    end_date=vacation_row.end_date)
                LOGGER.info(f"Found new vacation from Notion {vacation_row.name}")

                self._notion_manager.link_local_and_notion_entries(new_vacation.ref_id, vacation_row.notion_id)
                LOGGER.info(f"Linked the new vacation with local entries")

                vacation_row.ref_id = new_vacation.ref_id
                self._notion_manager.save_vacation(new_vacation.ref_id, vacation_row)
                LOGGER.info(f"Applies changes on Notion side too as {vacation_row}")

                vacations_rows_set[vacation_row.ref_id] = vacation_row
            elif vacation_row.ref_id in all_vacations_set and vacation_row.notion_id in all_vacations_notion_ids:
                vacation = all_vacations_set[EntityId(vacation_row.ref_id)]
                vacations_rows_set[EntityId(vacation_row.ref_id)] = vacation_row

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
                    if isinstance(vacation_row.start_date, pendulum.DateTime):
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should just start on a day")
                    if not vacation_row.end_date:
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should have an end date")
                    if isinstance(vacation_row.end_date, pendulum.DateTime):
                        raise ServiceValidationError(f"Vacation '{vacation_row.name}' should just end on a day")
                    if vacation_row.start_date >= vacation_row.end_date:
                        raise ServiceValidationError(
                            f"Start date for vacation {vacation_row.name} is after end date")

                    archived_time_action = \
                        TimeFieldAction.SET if not vacation.archived and vacation_row.archived else \
                        TimeFieldAction.CLEAR if vacation.archived and not vacation_row.archived else \
                        TimeFieldAction.DO_NOTHING
                    vacation.archived = vacation_row.archived
                    vacation.name = vacation_name
                    vacation.start_date = vacation_row.start_date
                    vacation.end_date = vacation_row.end_date
                    self._repository.update_vacation(vacation, archived_time_action=archived_time_action)
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
                self._notion_manager.hard_remove_vacation(vacation.ref_id)
                LOGGER.info(f"Removed vacation with id={vacation_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for vacation in all_vacations:
            if vacation.ref_id in vacations_rows_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue
            if vacation.archived:
                continue

            # If the vacation does not exist on Notion side, we create it.
            new_vacation_row = self._notion_manager.upsert_vacation(
                archived=vacation.archived,
                name=vacation.name,
                start_date=vacation.start_date,
                end_date=vacation.end_date,
                ref_id=vacation.ref_id)
            LOGGER.info(f"Created new vacation on Notion side {new_vacation_row}")

        return [self._row_to_entity(v) for v in all_vacations_set.values()]

    @staticmethod
    def _row_to_entity(row: VacationRow) -> Vacation:
        return Vacation(
            ref_id=row.ref_id,
            name=row.name,
            start_date=row.start_date,
            end_date=row.end_date,
            archived=row.archived)
