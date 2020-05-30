"""The service class for dealing with big plans."""
import logging
import uuid
from typing import Final, Iterable, Optional, Dict

import pendulum

from models.basic import EntityId, BasicValidator, ModelValidationError, BigPlanStatus, SyncPrefer
from remote.notion.big_plans import BigPlansCollection
from remote.notion.common import NotionPageLink, NotionCollectionLink
from repository.big_plans import BigPlan, BigPlansRepository
from service.errors import ServiceValidationError

LOGGER = logging.getLogger(__name__)


class BigPlansService:
    """The service class for dealing with big plans."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[BigPlansRepository]
    _collection: Final[BigPlansCollection]

    def __init__(
            self, basic_validator: BasicValidator, repository: BigPlansRepository,
            collection: BigPlansCollection) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._collection = collection

    def upsert_notion_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Upsert the Notion-side structure for inbox tasks."""
        return self._collection.upsert_big_plans_structure(project_ref_id, parent_page)

    def remove_notion_structure(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for inbox tasks."""
        for big_plan in self._repository.load_all_big_plans(filter_project_ref_ids=[project_ref_id]):
            self._repository.archive_big_plan(big_plan.ref_id)
        self._collection.remove_big_plans_structure(project_ref_id)

    def create_big_plan(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink, name: str,
            due_date: Optional[pendulum.DateTime]) -> BigPlan:
        """Create a big plan."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        new_big_plan = self._repository.create_big_plan(
            project_ref_id=project_ref_id,
            name=name,
            archived=False,
            status=BigPlanStatus.ACCEPTED,
            due_date=due_date,
            notion_link_uuid=uuid.uuid4())
        LOGGER.info("Applied local changes")
        self._collection.create_big_plan(
            project_ref_id=project_ref_id,
            inbox_collection_link=inbox_collection_link,
            name=new_big_plan.name,
            archived=new_big_plan.archived,
            due_date=new_big_plan.due_date,
            status=new_big_plan.status.for_notion(),
            ref_id=new_big_plan.ref_id)
        LOGGER.info("Applied Notion changes")

        return new_big_plan

    def archive_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Archive a big plan."""
        big_plan = self._repository.archive_big_plan(ref_id)
        LOGGER.info("Applied local changes")
        self._collection.archive_big_plan(big_plan.project_ref_id, ref_id)
        LOGGER.info("Applied Notion changes")

        return big_plan

    def set_big_plan_name(self, ref_id: EntityId, name: str) -> BigPlan:
        """Change the name of a big plan."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        big_plan = self._repository.load_big_plan(ref_id)
        big_plan.name = name
        self._repository.save_big_plan(big_plan)
        LOGGER.info("Applied local changes")

        big_plan_row = self._collection.load_big_plan(big_plan.project_ref_id, big_plan.ref_id)
        big_plan_row.name = name
        self._collection.save_big_plan(big_plan.project_ref_id, big_plan_row)
        LOGGER.info("Applied Notion changes")

        return big_plan

    def set_big_plan_status(
            self, ref_id: EntityId, status: BigPlanStatus) -> BigPlan:
        """Change the status of a big plan."""
        big_plan = self._repository.load_big_plan(ref_id)
        big_plan.status = status
        self._repository.save_big_plan(big_plan)
        LOGGER.info("Applied local changes")

        big_plan_row = self._collection.load_big_plan(big_plan.project_ref_id, big_plan.ref_id)
        big_plan_row.status = status.for_notion()
        self._collection.save_big_plan(big_plan.project_ref_id, big_plan_row)
        LOGGER.info("Applied Notion changes")

        return big_plan

    def set_big_plan_due_date(self, ref_id: EntityId, due_date: Optional[pendulum.DateTime]) -> BigPlan:
        """Change the due date of a big plan."""
        big_plan = self._repository.load_big_plan(ref_id)
        big_plan.due_date = due_date
        self._repository.save_big_plan(big_plan)
        LOGGER.info("Applied local changes")

        big_plan_row = self._collection.load_big_plan(big_plan.project_ref_id, big_plan.ref_id)
        big_plan_row.due_date = due_date
        self._collection.save_big_plan(big_plan.project_ref_id, big_plan_row)
        LOGGER.info("Applied Notion changes")

        return big_plan

    def load_all_big_plans(
            self, filter_archived: bool = True, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlan]:
        """Retrieve all big plans."""
        return self._repository.load_all_big_plans(
            filter_archived=filter_archived, filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)

    def load_big_plan_by_id(self, ref_id: EntityId) -> BigPlan:
        """Retrieve a big plan by id."""
        return self._repository.load_big_plan(ref_id)

    def big_plans_sync(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink,
            sync_prefer: SyncPrefer) -> Iterable[BigPlan]:
        """Synchronise big plans between Notion and local storage."""
        all_big_plans = self._repository.load_all_big_plans(
            filter_archived=False, filter_project_ref_ids=[project_ref_id])
        all_big_plans_set: Dict[EntityId, BigPlan] = {bp.ref_id: bp for bp in all_big_plans}

        all_big_plans_rows = self._collection.load_all_big_plans(project_ref_id)
        all_big_plans_rows_set = {}

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        for big_plan_row in all_big_plans_rows:
            LOGGER.info(f"Processing {big_plan_row}")
            if big_plan_row.ref_id is None or big_plan_row.ref_id == "":
                # If the big plan doesn't exist locally, we create it!
                try:
                    big_plan_name = self._basic_validator.entity_name_validate_and_clean(big_plan_row.name)
                    big_plan_status = self._basic_validator.big_plan_status_validate_and_clean(big_plan_row.status)\
                        if big_plan_row.status else BigPlanStatus.NOT_STARTED
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                new_big_plan = self._repository.create_big_plan(
                    project_ref_id=project_ref_id,
                    name=big_plan_name,
                    archived=big_plan_row.archived,
                    status=big_plan_status,
                    due_date=big_plan_row.due_date,
                    notion_link_uuid=uuid.uuid4())
                LOGGER.info(f"Found new big plan from Notion {big_plan_row.name}")

                self._collection.link_local_and_notion_entries(
                    project_ref_id, new_big_plan.ref_id, big_plan_row.notion_id)
                LOGGER.info(f"Linked the new big plan with local entries")

                big_plan_row.ref_id = new_big_plan.ref_id
                big_plan_row.status = new_big_plan.status.for_notion()
                self._collection.save_big_plan(
                    project_ref_id, big_plan_row, inbox_collection_link=inbox_collection_link)
                LOGGER.info(f"Applies changes on Notion side too as {big_plan_row}")

                all_big_plans_set[big_plan_row.ref_id] = new_big_plan
                all_big_plans_rows_set[big_plan_row.ref_id] = big_plan_row
            elif big_plan_row.ref_id in all_big_plans_set:
                # If the big plan exists locally, we sync it with the remote
                big_plan = all_big_plans_set[EntityId(big_plan_row.ref_id)]
                if sync_prefer == SyncPrefer.NOTION:
                    try:
                        big_plan_name = self._basic_validator.entity_name_validate_and_clean(big_plan_row.name)
                        big_plan_status = self._basic_validator.big_plan_status_validate_and_clean(
                            big_plan_row.status) \
                            if big_plan_row.status else BigPlanStatus.NOT_STARTED
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error
                    big_plan.name = big_plan_name
                    big_plan.archived = big_plan_row.archived
                    big_plan.status = big_plan_status
                    big_plan.due_date = big_plan.due_date
                    self._repository.save_big_plan(big_plan)
                    LOGGER.info(f"Changed big plan with id={big_plan_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    big_plan_row.name = big_plan.name
                    big_plan_row.archived = big_plan.archived
                    big_plan_row.status = big_plan.status.for_notion()
                    big_plan_row.due_date = big_plan.due_date
                    big_plan_row.ref_id = big_plan.ref_id
                    self._collection.save_big_plan(
                        project_ref_id, big_plan_row, inbox_collection_link=inbox_collection_link)
                    LOGGER.info(f"Changed big plan with id={big_plan_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
                all_big_plans_rows_set[EntityId(big_plan_row.ref_id)] = big_plan_row
            else:
                self._collection.hard_remove_big_plan(project_ref_id, EntityId(big_plan_row.ref_id))
                LOGGER.info(f"Removed dangling big plan in Notion {big_plan_row}")

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for big_plan in all_big_plans_set.values():
            # We've already processed this thing above
            if big_plan.ref_id in all_big_plans_rows_set:
                continue

            self._collection.create_big_plan(
                project_ref_id=project_ref_id,
                inbox_collection_link=inbox_collection_link,
                name=big_plan.name,
                archived=big_plan.archived,
                status=big_plan.status.value,
                due_date=big_plan.due_date,
                ref_id=big_plan.ref_id)
            LOGGER.info(f'Created Notion task for {big_plan.name}')

        return all_big_plans_set.values()