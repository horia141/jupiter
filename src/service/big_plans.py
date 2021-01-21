"""The service class for dealing with big plans."""
import logging
import uuid
from dataclasses import dataclass
from typing import Final, Iterable, Optional, Dict

import remote.notion.common
from models.basic import EntityId, BasicValidator, ModelValidationError, BigPlanStatus, SyncPrefer, ADate, Timestamp
from remote.notion.big_plans_manager import NotionBigPlansManager
from remote.notion.common import NotionPageLink, NotionCollectionLink, CollectionEntityNotFound
from repository.big_plans import BigPlanRow, BigPlansRepository
from service.errors import ServiceValidationError
from utils.time_field_action import TimeFieldAction

LOGGER = logging.getLogger(__name__)


@dataclass()
class BigPlansCollection:
    """A big plan collection attached to a project."""

    project_ref_id: EntityId


@dataclass()
class BigPlan:
    """A big plan."""

    ref_id: EntityId
    project_ref_id: EntityId
    archived: bool
    name: str
    status: BigPlanStatus
    due_date: Optional[ADate]
    notion_link_uuid: uuid.UUID
    created_time: Timestamp
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


class BigPlansService:
    """The service class for dealing with big plans."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[BigPlansRepository]
    _notion_manager: Final[NotionBigPlansManager]

    def __init__(
            self, basic_validator: BasicValidator, repository: BigPlansRepository,
            notion_manager: NotionBigPlansManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._notion_manager = notion_manager

    def create_big_plans_collection(self, project_ref_id: EntityId, parent_page: NotionPageLink) -> BigPlansCollection:
        """Create a big plan collection for a project."""
        self._notion_manager.upsert_big_plan_collection(project_ref_id, parent_page)
        return BigPlansCollection(project_ref_id=project_ref_id)

    def upsert_big_plans_collection_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> None:
        """Upsert the Notion-side structure for inbox tasks."""
        self._notion_manager.upsert_big_plan_collection(project_ref_id, parent_page)

    def archive_big_plans_collection(self, project_ref_id: EntityId) -> BigPlansCollection:
        """Remove the Notion-side structure for inbox tasks."""
        for big_plan in self._repository.find_all_big_plans(filter_project_ref_ids=[project_ref_id]):
            self._repository.archive_big_plan(big_plan.ref_id)
        self._notion_manager.remove_big_plans_collection(project_ref_id)
        return BigPlansCollection(project_ref_id=project_ref_id)

    def create_big_plan(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink, name: str,
            due_date: Optional[ADate]) -> BigPlan:
        """Create a big plan."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        new_big_plan_row = self._repository.create_big_plan(
            project_ref_id=project_ref_id,
            name=name,
            archived=False,
            status=BigPlanStatus.ACCEPTED,
            due_date=due_date,
            notion_link_uuid=uuid.uuid4())
        LOGGER.info("Applied local changes")
        self._notion_manager.upsert_big_plan(
            project_ref_id=project_ref_id,
            inbox_collection_link=inbox_collection_link,
            name=new_big_plan_row.name,
            archived=new_big_plan_row.archived,
            due_date=new_big_plan_row.due_date,
            status=new_big_plan_row.status.for_notion(),
            ref_id=new_big_plan_row.ref_id)
        LOGGER.info("Applied Notion changes")

        return BigPlan(
            ref_id=new_big_plan_row.ref_id,
            project_ref_id=new_big_plan_row.project_ref_id,
            archived=new_big_plan_row.archived,
            name=new_big_plan_row.name,
            status=new_big_plan_row.status,
            due_date=new_big_plan_row.due_date,
            notion_link_uuid=new_big_plan_row.notion_link_uuid,
            created_time=new_big_plan_row.created_time,
            accepted_time=new_big_plan_row.accepted_time,
            working_time=new_big_plan_row.working_time,
            completed_time=new_big_plan_row.completed_time)

    def archive_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Archive a big plan."""
        big_plan_row = self._repository.archive_big_plan(ref_id)
        LOGGER.info("Applied local changes")
        try:
            self._notion_manager.archive_big_plan(big_plan_row.project_ref_id, ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival of Notion big plan because it could not be found")

        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def archive_done_big_plans(self, filter_project_ref_id: Optional[Iterable[EntityId]] = None) -> None:
        """Archive the done big plans."""
        big_plans = self._repository.find_all_big_plans(
            allow_archived=False, filter_project_ref_ids=filter_project_ref_id)

        for big_plan in big_plans:
            if big_plan.archived:
                continue

            if not big_plan.status.is_completed:
                continue

            LOGGER.info(f"Removing task '{big_plan.name}'")
            self._repository.archive_big_plan(big_plan.ref_id)
            try:
                self._notion_manager.archive_big_plan(big_plan.project_ref_id, big_plan.ref_id)
            except remote.notion.common.CollectionEntityNotFound:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping archival on Notion side because big plan was not found")

    def set_big_plan_name(self, ref_id: EntityId, name: str) -> BigPlan:
        """Change the name of a big plan."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        big_plan_row = self._repository.load_big_plan(ref_id)
        big_plan_row.name = name
        self._repository.update_big_plan(big_plan_row)
        LOGGER.info("Applied local changes")

        big_plan_notion_row = self._notion_manager.load_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id)
        big_plan_notion_row.name = name
        self._notion_manager.save_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id, big_plan_notion_row)
        LOGGER.info("Applied Notion changes")

        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def set_big_plan_status(
            self, ref_id: EntityId, status: BigPlanStatus) -> BigPlan:
        """Change the status of a big plan."""
        big_plan_row = self._repository.load_big_plan(ref_id)
        accepted_time_action = \
            TimeFieldAction.SET if not big_plan_row.status.is_accepted_or_more and status.is_accepted_or_more else \
            TimeFieldAction.CLEAR if big_plan_row.status.is_accepted_or_more and not status.is_accepted_or_more else \
            TimeFieldAction.DO_NOTHING
        working_time_action = \
            TimeFieldAction.SET if not big_plan_row.status.is_working_or_more and status.is_working_or_more else \
            TimeFieldAction.CLEAR if big_plan_row.status.is_working_or_more and not status.is_working_or_more else \
            TimeFieldAction.DO_NOTHING
        completed_time_action = \
            TimeFieldAction.SET if not big_plan_row.status.is_completed and status.is_completed else \
            TimeFieldAction.CLEAR if big_plan_row.status.is_completed and not status.is_completed else \
            TimeFieldAction.DO_NOTHING
        big_plan_row.status = status
        self._repository.update_big_plan(
            big_plan_row, accepted_time_action=accepted_time_action, working_time_action=working_time_action,
            completed_time_action=completed_time_action)
        LOGGER.info("Applied local changes")

        big_plan_notion_row = self._notion_manager.load_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id)
        big_plan_notion_row.status = status.for_notion()
        self._notion_manager.save_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id, big_plan_notion_row)
        LOGGER.info("Applied Notion changes")

        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def set_big_plan_due_date(self, ref_id: EntityId, due_date: Optional[ADate]) -> BigPlan:
        """Change the due date of a big plan."""
        big_plan_row = self._repository.load_big_plan(ref_id)
        big_plan_row.due_date = due_date
        self._repository.update_big_plan(big_plan_row)
        LOGGER.info("Applied local changes")

        big_plan_notion_row = self._notion_manager.load_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id)
        big_plan_notion_row.due_date = due_date
        self._notion_manager.save_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id, big_plan_notion_row)
        LOGGER.info("Applied Notion changes")

        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def hard_remove_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Hard remove an big plan."""
        # Apply changes locally
        big_plan_row = self._repository.remove_big_plan(ref_id)
        LOGGER.info("Applied local changes")
        try:
            self._notion_manager.hard_remove_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping hard removal on Notion side since big plan could not be found")

        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def remove_big_plan_on_notion_side(self, ref_id: EntityId) -> BigPlan:
        """Remove entries for a big plan on Notion-side."""
        big_plan_row = self._repository.load_big_plan(ref_id, allow_archived=True)
        try:
            self._notion_manager.hard_remove_big_plan(big_plan_row.project_ref_id, big_plan_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping removal on Notion side because big plan was not found")

        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def load_all_big_plans(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlan]:
        """Retrieve all big plans."""
        big_plan_rows = self._repository.find_all_big_plans(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)
        return [BigPlan(
            ref_id=bp.ref_id,
            project_ref_id=bp.project_ref_id,
            archived=bp.archived,
            name=bp.name,
            status=bp.status,
            due_date=bp.due_date,
            notion_link_uuid=bp.notion_link_uuid,
            created_time=bp.created_time,
            accepted_time=bp.accepted_time,
            working_time=bp.working_time,
            completed_time=bp.completed_time) for bp in big_plan_rows]

    def load_all_recurring_tasks_not_notion_gced(self, project_ref_ids: EntityId) -> Iterable[BigPlan]:
        """Retrieve all big plans which have not been gc-ed on Notion side."""
        allowed_ref_ids = self._notion_manager.load_all_saved_big_plans_ref_ids(project_ref_ids)
        big_plan_rows = \
            [it for it in self._repository.find_all_big_plans(
                allow_archived=True, filter_project_ref_ids=[project_ref_ids])
             if it.ref_id in allowed_ref_ids]
        return [BigPlan(
            ref_id=bp.ref_id,
            project_ref_id=bp.project_ref_id,
            archived=bp.archived,
            name=bp.name,
            status=bp.status,
            due_date=bp.due_date,
            notion_link_uuid=bp.notion_link_uuid,
            created_time=bp.created_time,
            accepted_time=bp.accepted_time,
            working_time=bp.working_time,
            completed_time=bp.completed_time) for bp in big_plan_rows]

    def load_big_plan_by_id(self, ref_id: EntityId) -> BigPlan:
        """Retrieve a big plan by id."""
        big_plan_row = self._repository.load_big_plan(ref_id)
        return BigPlan(
            ref_id=big_plan_row.ref_id,
            project_ref_id=big_plan_row.project_ref_id,
            archived=big_plan_row.archived,
            name=big_plan_row.name,
            status=big_plan_row.status,
            due_date=big_plan_row.due_date,
            notion_link_uuid=big_plan_row.notion_link_uuid,
            created_time=big_plan_row.created_time,
            accepted_time=big_plan_row.accepted_time,
            working_time=big_plan_row.working_time,
            completed_time=big_plan_row.completed_time)

    def big_plans_sync(
            self, project_ref_id: EntityId, drop_all_notion_side: bool, inbox_collection_link: NotionCollectionLink,
            sync_even_if_not_modified: bool, filter_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[BigPlan]:
        """Synchronise big plans between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        all_big_plans = self._repository.find_all_big_plans(
            allow_archived=True, filter_ref_ids=filter_ref_ids, filter_project_ref_ids=[project_ref_id])
        all_big_plans_set: Dict[EntityId, BigPlanRow] = {bp.ref_id: bp for bp in all_big_plans}

        if not drop_all_notion_side:
            all_big_plans_notion_rows = self._notion_manager.load_all_big_plans(project_ref_id)
            all_big_plans_notion_ids = \
                set(self._notion_manager.load_all_saved_big_plans_notion_ids(project_ref_id))
        else:
            self._notion_manager.drop_all_big_plans(project_ref_id)
            all_big_plans_notion_rows = {}
            all_big_plans_notion_ids = set()
        all_big_plans_rows_set = {}

        # Then look at each big plan in Notion and try to match it with the one in the local stash

        for big_plan_notion_row in all_big_plans_notion_rows:
            # Skip this step when asking only for particular entities to be synced.
            if filter_ref_ids_set is not None and big_plan_notion_row.ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{big_plan_notion_row.name}' (id={big_plan_notion_row.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{big_plan_notion_row.name}' (id={big_plan_notion_row.notion_id})")
            if big_plan_notion_row.ref_id is None or big_plan_notion_row.ref_id == "":
                # If the big plan doesn't exist locally, we create it!
                try:
                    big_plan_name = self._basic_validator.entity_name_validate_and_clean(big_plan_notion_row.name)
                    big_plan_status = \
                        self._basic_validator.big_plan_status_validate_and_clean(big_plan_notion_row.status)\
                            if big_plan_notion_row.status else BigPlanStatus.NOT_STARTED
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                new_big_plan = self._repository.create_big_plan(
                    project_ref_id=project_ref_id,
                    name=big_plan_name,
                    archived=big_plan_notion_row.archived,
                    status=big_plan_status,
                    due_date=big_plan_notion_row.due_date,
                    notion_link_uuid=uuid.uuid4())
                LOGGER.info(f"Found new big plan from Notion {big_plan_notion_row.name}")

                self._notion_manager.link_local_and_notion_entries(
                    project_ref_id, new_big_plan.ref_id, big_plan_notion_row.notion_id)
                LOGGER.info(f"Linked the new big plan with local entries")

                big_plan_notion_row.ref_id = new_big_plan.ref_id
                big_plan_notion_row.status = new_big_plan.status.for_notion()
                self._notion_manager.save_big_plan(
                    project_ref_id, big_plan_notion_row.ref_id, big_plan_notion_row, inbox_collection_link)
                LOGGER.info(f"Applies changes on Notion side too as {big_plan_notion_row}")

                all_big_plans_set[big_plan_notion_row.ref_id] = new_big_plan
                all_big_plans_rows_set[big_plan_notion_row.ref_id] = big_plan_notion_row
            elif big_plan_notion_row.ref_id in all_big_plans_set and \
                    big_plan_notion_row.notion_id in all_big_plans_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                big_plan = all_big_plans_set[EntityId(big_plan_notion_row.ref_id)]
                all_big_plans_rows_set[EntityId(big_plan_notion_row.ref_id)] = big_plan_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and big_plan_notion_row.last_edited_time <= big_plan.last_modified_time:
                        LOGGER.info(f"Skipping {big_plan_notion_row.name} because it was not modified")
                        continue

                    try:
                        big_plan_name = self._basic_validator.entity_name_validate_and_clean(big_plan_notion_row.name)
                        big_plan_status = self._basic_validator.big_plan_status_validate_and_clean(
                            big_plan_notion_row.status) \
                            if big_plan_notion_row.status else BigPlanStatus.NOT_STARTED
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    archived_time_action = \
                        TimeFieldAction.SET if not big_plan.archived and big_plan_notion_row.archived else \
                        TimeFieldAction.CLEAR if big_plan.archived and not big_plan_notion_row.archived else \
                        TimeFieldAction.DO_NOTHING
                    accepted_time_action = \
                        TimeFieldAction.SET if \
                            (not big_plan.status.is_accepted_or_more and big_plan_status.is_accepted_or_more) else \
                        TimeFieldAction.CLEAR if \
                            (big_plan.status.is_accepted_or_more and not big_plan_status.is_accepted_or_more) else \
                        TimeFieldAction.DO_NOTHING
                    working_time_action = \
                        TimeFieldAction.SET if \
                            (not big_plan.status.is_working_or_more and big_plan_status.is_working_or_more) else \
                        TimeFieldAction.CLEAR if \
                            (big_plan.status.is_working_or_more and not big_plan_status.is_working_or_more) else \
                        TimeFieldAction.DO_NOTHING
                    completed_time_action = \
                        TimeFieldAction.SET if \
                            (not big_plan.status.is_completed and big_plan_status.is_completed) else \
                        TimeFieldAction.CLEAR if \
                            (big_plan.status.is_completed and not big_plan_status.is_completed) else \
                        TimeFieldAction.DO_NOTHING
                    big_plan.name = big_plan_name
                    big_plan.archived = big_plan_notion_row.archived
                    big_plan.status = big_plan_status
                    big_plan.due_date = big_plan.due_date
                    self._repository.update_big_plan(
                        big_plan, archived_time_action=archived_time_action,
                        accepted_time_action=accepted_time_action, working_time_action=working_time_action,
                        completed_time_action=completed_time_action)
                    LOGGER.info(f"Changed big plan with id={big_plan_notion_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            big_plan.last_modified_time <= big_plan_notion_row.last_edited_time:
                        LOGGER.info(f"Skipping {big_plan.name} because it was not modified")
                        continue

                    big_plan_notion_row.name = big_plan.name
                    big_plan_notion_row.archived = big_plan.archived
                    big_plan_notion_row.status = big_plan.status.for_notion()
                    big_plan_notion_row.due_date = big_plan.due_date
                    big_plan_notion_row.ref_id = big_plan.ref_id
                    self._notion_manager.save_big_plan(
                        project_ref_id, big_plan.ref_id, big_plan_notion_row, inbox_collection_link)
                    LOGGER.info(f"Changed big plan with id={big_plan_notion_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random big plan added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a big plan added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_big_plan(project_ref_id, big_plan_notion_row.ref_id)
                LOGGER.info(f"Removed dangling big plan in Notion {big_plan_notion_row}")

        LOGGER.info("Applied local changes")

        # Now, go over each local big plan, and add it to Notion if it doesn't
        # exist there!

        for big_plan in all_big_plans_set.values():
            # We've already processed this thing above
            if big_plan.ref_id in all_big_plans_rows_set:
                continue
            if big_plan.archived:
                continue

            self._notion_manager.upsert_big_plan(
                project_ref_id=project_ref_id,
                inbox_collection_link=inbox_collection_link,
                name=big_plan.name,
                archived=big_plan.archived,
                status=big_plan.status.for_notion(),
                due_date=big_plan.due_date,
                ref_id=big_plan.ref_id)
            LOGGER.info(f'Created Notion task for {big_plan.name}')

        return [BigPlan(
            ref_id=bp.ref_id,
            project_ref_id=bp.project_ref_id,
            archived=bp.archived,
            name=bp.name,
            status=bp.status,
            due_date=bp.due_date,
            notion_link_uuid=bp.notion_link_uuid,
            created_time=bp.created_time,
            accepted_time=bp.accepted_time,
            working_time=bp.working_time,
            completed_time=bp.completed_time) for bp in all_big_plans_set.values()]
