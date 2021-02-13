"""The service class for dealing with inbox tasks."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, List, Iterable

import pendulum
from pendulum import UTC

import remote.notion.common
from models.basic import BasicValidator, EntityId, ModelValidationError, InboxTaskStatus, Eisen, Difficulty, \
    SyncPrefer, RecurringTaskPeriod, RecurringTaskType, ADate, Timestamp
from remote.notion.common import NotionPageLink, NotionCollectionLink
from remote.notion.inbox_tasks_manager import NotionInboxTasksManager, InboxTaskBigPlanLabel
from repository.inbox_tasks import InboxTasksRepository, InboxTaskRow
from service.errors import ServiceValidationError
from utils.time_field_action import TimeFieldAction

LOGGER = logging.getLogger(__name__)


@dataclass()
class InboxTasksCollection:
    """The inbox tasks collection attached to a project."""

    project_ref_id: EntityId
    notion_collection: NotionCollectionLink


@dataclass()
class InboxTask:
    """An inbox tasks."""

    ref_id: EntityId
    project_ref_id: EntityId
    big_plan_ref_id: Optional[EntityId]
    recurring_task_ref_id: Optional[EntityId]
    archived: bool
    name: str
    status: InboxTaskStatus
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    recurring_task_timeline: Optional[str]
    recurring_task_type: Optional[RecurringTaskType]
    recurring_task_gen_right_now: Optional[Timestamp]  # Time for which this inbox task was generated
    created_time: Timestamp
    last_modified_time: Timestamp
    accepted_time: Optional[Timestamp]
    working_time: Optional[Timestamp]
    completed_time: Optional[Timestamp]


@dataclass()
class BigPlanEssentials:
    """Essential info about a big plan."""

    ref_id: EntityId
    name: str


@dataclass()
class RecurringTaskEssentials:
    """Essential info about a recurring task."""

    ref_id: EntityId
    name: str
    period: RecurringTaskPeriod
    the_type: RecurringTaskType


class InboxTasksService:
    """The service class for dealing with inbox tasks."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[InboxTasksRepository]
    _notion_manager: Final[NotionInboxTasksManager]

    def __init__(
            self, basic_validator: BasicValidator, repository: InboxTasksRepository,
            notion_manager: NotionInboxTasksManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._notion_manager = notion_manager

    def create_inbox_tasks_collection(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> InboxTasksCollection:
        """Create an inbox tasks collection for a project."""
        inbox_tasks_collection = self._notion_manager.upsert_inbox_task_collection(project_ref_id, parent_page)
        return InboxTasksCollection(
            project_ref_id=project_ref_id, notion_collection=inbox_tasks_collection.notion_link)

    def upsert_inbox_tasks_collection_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Upsert the Notion-side structure for inbox tasks."""
        return self._notion_manager.upsert_inbox_task_collection(project_ref_id, parent_page).notion_link

    def archive_inbox_tasks_collection(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for inbox tasks."""
        for inbox_task in self._repository.find_all_inbox_tasks(filter_project_ref_ids=[project_ref_id]):
            self._repository.archive_inbox_task(inbox_task.ref_id)
        self._notion_manager.remove_inbox_tasks_collection(project_ref_id)

    def get_inbox_tasks_collection(self, project_ref_id: EntityId) -> InboxTasksCollection:
        """Retrieve the Notion-side structure link."""
        notion_link = self._notion_manager.get_inbox_tasks_structure(project_ref_id)
        return InboxTasksCollection(
            project_ref_id=project_ref_id,
            notion_collection=NotionCollectionLink(
                page_id=notion_link.page_id,
                collection_id=notion_link.collection_id))

    def upsert_notion_big_plan_ref_options(
            self, project_ref_id: EntityId, big_plan_labels: Iterable[InboxTaskBigPlanLabel]) -> None:
        """Upsert the Notion-side structure for the 'big plan' field options."""
        self._notion_manager.upsert_inbox_tasks_big_plan_field_options(project_ref_id, big_plan_labels)

    def create_inbox_task(
            self, project_ref_id: EntityId, name: str, big_plan_ref_id: Optional[EntityId],
            big_plan_name: Optional[str], eisen: List[Eisen], difficulty: Optional[Difficulty],
            actionable_date: Optional[ADate], due_date: Optional[ADate]) -> InboxTask:
        """Create an inbox task."""
        if big_plan_ref_id is None and big_plan_name is not None:
            raise ServiceValidationError(f"Should have null name for null big plan for task")
        if big_plan_ref_id is not None and big_plan_name is None:
            raise ServiceValidationError(f"Should have non-null name for non-null big plan for task")

        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        self._check_actionable_and_due_dates(actionable_date, due_date)

        # Apply changes locally
        new_inbox_task_row = self._repository.create_inbox_task(
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            recurring_task_ref_id=None,
            name=name,
            archived=False,
            status=InboxTaskStatus.ACCEPTED,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_task_timeline=None,
            recurring_task_type=None,
            recurring_task_gen_right_now=None)
        LOGGER.info("Applied local changes")
        # Apply Notion changes
        self._notion_manager.upsert_inbox_task(
            project_ref_id=project_ref_id,
            name=new_inbox_task_row.name,
            archived=False,
            big_plan_ref_id=new_inbox_task_row.big_plan_ref_id,
            big_plan_name=remote.notion.common.format_name_for_option(
                big_plan_name) if big_plan_name else None,
            recurring_task_ref_id=None,
            status=new_inbox_task_row.status.for_notion(),
            eisen=[e.for_notion() for e in new_inbox_task_row.eisen],
            difficulty=new_inbox_task_row.difficulty.for_notion() if new_inbox_task_row.difficulty else None,
            actionable_date=new_inbox_task_row.actionable_date,
            due_date=new_inbox_task_row.due_date,
            recurring_timeline=None,
            recurring_period=None,
            recurring_task_type=None,
            recurring_task_gen_right_now=None,
            ref_id=new_inbox_task_row.ref_id)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(new_inbox_task_row)

    def create_inbox_task_for_recurring_task(
            self, project_ref_id: EntityId, name: str, recurring_task_ref_id: EntityId,
            recurring_task_timeline: str, recurring_task_period: RecurringTaskPeriod,
            recurring_task_type: RecurringTaskType, recurring_task_gen_right_now: Timestamp, eisen: List[Eisen],
            difficulty: Optional[Difficulty], actionable_date: Optional[ADate], due_date: Optional[ADate]) -> InboxTask:
        """Create an inbox task."""
        # Apply changes locally
        new_inbox_task_row = self._repository.create_inbox_task(
            project_ref_id=project_ref_id,
            big_plan_ref_id=None,
            recurring_task_ref_id=recurring_task_ref_id,
            name=name,
            archived=False,
            status=InboxTaskStatus.RECURRING,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            recurring_task_timeline=recurring_task_timeline,
            recurring_task_type=recurring_task_type,
            recurring_task_gen_right_now=recurring_task_gen_right_now)
        LOGGER.info("Applied local changes")
        # Apply Notion changes
        self._notion_manager.upsert_inbox_task(
            project_ref_id=project_ref_id,
            name=new_inbox_task_row.name,
            archived=False,
            big_plan_ref_id=None,
            big_plan_name=None,
            recurring_task_ref_id=new_inbox_task_row.recurring_task_ref_id,
            status=new_inbox_task_row.status.for_notion(),
            eisen=[e.for_notion() for e in new_inbox_task_row.eisen],
            difficulty=new_inbox_task_row.difficulty.for_notion() if new_inbox_task_row.difficulty else None,
            actionable_date=new_inbox_task_row.actionable_date,
            due_date=new_inbox_task_row.due_date,
            recurring_timeline=new_inbox_task_row.recurring_task_timeline,
            recurring_period=recurring_task_period.value,
            recurring_task_type=recurring_task_type.value,
            recurring_task_gen_right_now=recurring_task_gen_right_now,
            ref_id=new_inbox_task_row.ref_id)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(new_inbox_task_row)

    def archive_inbox_task(self, ref_id: EntityId) -> InboxTask:
        """Archive an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.archive_inbox_task(ref_id)
        LOGGER.info("Applied local changes")
        # Apply Notion changes
        try:
            self._notion_manager.archive_inbox_task(inbox_task_row.project_ref_id, ref_id)
            LOGGER.info("Applied Notion changes")
        except remote.notion.common.CollectionEntityNotFound:
            LOGGER.info("Skipping archiving of Notion inbox task because it could not be found")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_name(self, ref_id: EntityId, name: str) -> InboxTask:
        """Change the name of an inbox task."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        if inbox_task_row.recurring_task_ref_id is not None:
            raise ServiceValidationError(
                f"Cannot modify name of task created from recurring task '{inbox_task_row.name}'")
        inbox_task_row.name = name
        self._repository.update_inbox_task(inbox_task_row)
        LOGGER.info("Modified inbox task locally")

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.name = name
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def associate_inbox_task_with_big_plan(
            self, ref_id: EntityId, big_plan_ref_id: Optional[EntityId], big_plan_name: Optional[str]) -> InboxTask:
        """Associate an inbox task with a big plan."""
        if big_plan_ref_id is None and big_plan_name is not None:
            raise ServiceValidationError(f"Should have null name for null big plan for task with id='{ref_id}'")
        if big_plan_ref_id is not None and big_plan_name is None:
            raise ServiceValidationError(f"Should have non-null name for non-null big plan for task with id='{ref_id}'")

        try:
            big_plan_name = self._basic_validator.entity_name_validate_and_clean(big_plan_name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        if inbox_task_row.recurring_task_ref_id is not None:
            raise ServiceValidationError(
                f"Cannot associate with a big plan a task created from recurring task '{inbox_task_row.name}'")
        inbox_task_row.big_plan_ref_id = big_plan_ref_id
        self._repository.update_inbox_task(inbox_task_row)

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.big_plan_ref_id = big_plan_ref_id
        inbox_task_notion_row.big_plan_name = \
            remote.notion.common.format_name_for_option(big_plan_name) if big_plan_name else None
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_to_big_plan_link(
            self, ref_id: EntityId, big_plan_ref_id: EntityId, big_plan_name: str) -> InboxTask:
        """Change the parameters of the link between the big plan and the inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id, allow_archived=True)
        if inbox_task_row.big_plan_ref_id != big_plan_ref_id:
            raise ServiceValidationError(
                f"Cannot reassociate a task which is not with the big plan '{inbox_task_row.name}'")

        # Apply changes in Notion
        try:
            inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
            inbox_task_notion_row.big_plan_ref_id = big_plan_ref_id
            inbox_task_notion_row.big_plan_name = remote.notion.common.format_name_for_option(big_plan_name)
            self._notion_manager.save_inbox_task(
                inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
            LOGGER.info("Applied Notion changes")
        except remote.notion.common.CollectionEntityNotFound:
            LOGGER.info(
                f"Skipping updating link of ref_id='{inbox_task_row.ref_id}' because it could not be found")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_to_recurring_task_link(
            self, ref_id: EntityId, name: str, timeline: str, period: RecurringTaskPeriod, the_type: RecurringTaskType,
            actionable_date: ADate, due_time: ADate, eisen: List[Eisen], difficulty: Optional[Difficulty]) -> InboxTask:
        """Change the parameters of the link between the inbox task as an instance of a recurring task."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id, allow_archived=True)
        if inbox_task_row.recurring_task_ref_id is None:
            raise ServiceValidationError(
                f"Cannot associate a task which is not recurring with a recurring one '{inbox_task_row.name}'")
        inbox_task_row.name = name
        inbox_task_row.actionable_date = actionable_date
        inbox_task_row.due_date = due_time
        inbox_task_row.eisen = eisen
        inbox_task_row.difficulty = difficulty
        inbox_task_row.recurring_task_timeline = timeline
        inbox_task_row.recurring_task_type = the_type
        self._repository.update_inbox_task(inbox_task_row)
        LOGGER.info("Modified inbox task locally")

        # Apply changes in Notion
        try:
            inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
            inbox_task_notion_row.name = name
            inbox_task_notion_row.actionable_date = actionable_date
            inbox_task_notion_row.due_date = due_time
            inbox_task_notion_row.eisen = [e.value for e in eisen]
            inbox_task_notion_row.difficulty = difficulty.value if difficulty else None
            inbox_task_notion_row.recurring_timeline = timeline
            inbox_task_notion_row.recurring_period = period.value
            inbox_task_notion_row.recurring_task_type = the_type.value
            self._notion_manager.save_inbox_task(
                inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
            LOGGER.info("Applied Notion changes")
        except remote.notion.common.CollectionEntityNotFound:
            LOGGER.info(
                f"Skipping updating link of ref_id='{inbox_task_row.ref_id}' because it could not be found")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_status(self, ref_id: EntityId, status: InboxTaskStatus) -> InboxTask:
        """Change the status of an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        accepted_time_action = \
            TimeFieldAction.SET if not inbox_task_row.status.is_accepted_or_more and status.is_accepted_or_more else \
            TimeFieldAction.CLEAR if inbox_task_row.status.is_accepted_or_more and not status.is_accepted_or_more else \
            TimeFieldAction.DO_NOTHING
        working_time_action = \
            TimeFieldAction.SET if not inbox_task_row.status.is_working_or_more and status.is_working_or_more else \
            TimeFieldAction.CLEAR if inbox_task_row.status.is_working_or_more and not status.is_working_or_more else \
            TimeFieldAction.DO_NOTHING
        completed_time_action = \
            TimeFieldAction.SET if not inbox_task_row.status.is_completed and status.is_completed else \
            TimeFieldAction.CLEAR if inbox_task_row.status.is_completed and not status.is_completed else \
            TimeFieldAction.DO_NOTHING
        inbox_task_row.status = status
        self._repository.update_inbox_task(
            inbox_task_row, accepted_time_action=accepted_time_action, working_time_action=working_time_action,
            completed_time_action=completed_time_action)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.status = status.for_notion()
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_actionable_date(self, ref_id: EntityId, actionable_date: Optional[ADate]) -> InboxTask:
        """Change the due date of an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        self._check_actionable_and_due_dates(actionable_date, inbox_task_row.due_date)
        inbox_task_row.actionable_date = actionable_date
        self._repository.update_inbox_task(inbox_task_row)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.actionable_date = actionable_date
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_due_date(self, ref_id: EntityId, due_date: Optional[ADate]) -> InboxTask:
        """Change the due date of an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        self._check_actionable_and_due_dates(inbox_task_row.actionable_date, due_date)
        inbox_task_row.due_date = due_date
        self._repository.update_inbox_task(inbox_task_row)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.due_date = due_date
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> InboxTask:
        """Change the Eisenhower status of an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        if inbox_task_row.recurring_task_ref_id is None:
            raise ServiceValidationError(
                f"Cannot change the Eisenhower status of a task created from a recurring one '{inbox_task_row.name}'")
        inbox_task_row.eisen = eisen
        self._repository.update_inbox_task(inbox_task_row)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.eisen = [e.value for e in eisen]
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def set_inbox_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> InboxTask:
        """Change the difficulty of an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.load_inbox_task(ref_id)
        if inbox_task_row.recurring_task_ref_id is None:
            raise ServiceValidationError(
                f"Cannot change the difficulty of a task created from a recurring one '{inbox_task_row.name}'")
        inbox_task_row.difficulty = difficulty
        self._repository.update_inbox_task(inbox_task_row)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion
        inbox_task_notion_row = self._notion_manager.load_inbox_task(inbox_task_row.project_ref_id, ref_id)
        inbox_task_notion_row.difficulty = difficulty.value if difficulty else None
        self._notion_manager.save_inbox_task(
            inbox_task_row.project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(inbox_task_row)

    def hard_remove_inbox_task(self, ref_id: EntityId) -> InboxTask:
        """Hard remove an inbox task."""
        # Apply changes locally
        inbox_task_row = self._repository.remove_inbox_task(ref_id)
        LOGGER.info("Applied local changes")
        try:
            self._notion_manager.hard_remove_inbox_task(inbox_task_row.project_ref_id, inbox_task_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except remote.notion.common.CollectionEntityNotFound:
            LOGGER.info("Skipping hard removal on Notion side since inbox task could not be found")

        return self._row_to_entity(inbox_task_row)

    def remove_inbox_task_on_notion_side(self, ref_id: EntityId) -> InboxTask:
        """Remove entries for a inbox task on Notion-side."""
        inbox_task_row = self._repository.load_inbox_task(ref_id, allow_archived=True)
        try:
            self._notion_manager.hard_remove_inbox_task(inbox_task_row.project_ref_id, inbox_task_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except remote.notion.common.CollectionEntityNotFound:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because inbox task was not found")

        return self._row_to_entity(inbox_task_row)

    def archive_done_inbox_tasks(self, filter_project_ref_id: Optional[Iterable[EntityId]] = None) -> None:
        """Archive the done inbox tasks."""
        inbox_task_rows = self._repository.find_all_inbox_tasks(
            allow_archived=False, filter_project_ref_ids=filter_project_ref_id)

        for inbox_task_row in inbox_task_rows:
            if not inbox_task_row.status.is_completed:
                continue

            LOGGER.info(f"Removing task '{inbox_task_row.name}'")
            self._repository.archive_inbox_task(inbox_task_row.ref_id)
            try:
                self._notion_manager.archive_inbox_task(inbox_task_row.project_ref_id, inbox_task_row.ref_id)
            except remote.notion.common.CollectionEntityNotFound:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping archival on Notion side because inbox task was not found")

    def load_all_inbox_tasks(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTask]:
        """Retrieve all inbox tasks."""
        inbox_task_rows = self._repository.find_all_inbox_tasks(
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_big_plan_ref_ids=filter_big_plan_ref_ids,
            filter_recurring_task_ref_ids=filter_recurring_task_ref_ids)
        return [self._row_to_entity(it) for it in inbox_task_rows]

    def load_all_inbox_tasks_not_notion_gced(self, project_ref_ids: EntityId) -> Iterable[InboxTask]:
        """Retrieve all inbox tasks which have not been gc-ed on Notion side."""
        allowed_ref_ids = self._notion_manager.load_all_saved_inbox_tasks_ref_ids(project_ref_ids)
        inbox_task_rows = \
            [it for it in self._repository.find_all_inbox_tasks(
                allow_archived=True, filter_project_ref_ids=[project_ref_ids])
             if it.ref_id in allowed_ref_ids]
        return [self._row_to_entity(it) for it in inbox_task_rows]

    def inbox_tasks_sync(
            self, project_ref_id: EntityId, drop_all_notion_side: bool,
            all_big_plans: Iterable[BigPlanEssentials], all_recurring_tasks: Iterable[RecurringTaskEssentials],
            sync_even_if_not_modified: bool, filter_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[InboxTask]:
        """Synchronise the inbox tasks between the Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        all_inbox_task_rows = self._repository.find_all_inbox_tasks(
            allow_archived=True, filter_ref_ids=filter_ref_ids, filter_project_ref_ids=[project_ref_id])
        all_inbox_task_rows_set = {rt.ref_id: rt for rt in all_inbox_task_rows}

        if not drop_all_notion_side:
            all_inbox_task_notion_rows = self._notion_manager.load_all_inbox_tasks(project_ref_id)
            all_inbox_task_notion_ids = \
                set(self._notion_manager.load_all_saved_inbox_tasks_notion_ids(project_ref_id))
        else:
            self._notion_manager.drop_all_inbox_tasks(project_ref_id)
            all_inbox_task_notion_rows = {}
            all_inbox_task_notion_ids = set()
        all_inbox_tasks_notion_row_set = {}

        all_big_plans_by_name = \
            {remote.notion.common.format_name_for_option(
                self._basic_validator.entity_name_validate_and_clean(bp.name)): bp for bp in all_big_plans}

        all_big_plans_map = {bp.ref_id: bp for bp in all_big_plans}
        all_recurring_tasks_map = {rt.ref_id: rt for rt in all_recurring_tasks}

        # Prepare Notion connection

        for inbox_task_notion_row in all_inbox_task_notion_rows:
            # Skip this step when asking only for particular entities to be synced.
            if filter_ref_ids_set is not None and inbox_task_notion_row.ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{inbox_task_notion_row.name}' " +
                    f"(id={inbox_task_notion_row.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{inbox_task_notion_row.name}' (id={inbox_task_notion_row.notion_id})")

            if inbox_task_notion_row.ref_id is None or inbox_task_notion_row.ref_id == "":
                # If the big plan doesn't exist locally, we create it!

                try:
                    inbox_task_name = self._basic_validator.entity_name_validate_and_clean(inbox_task_notion_row.name)
                    inbox_task_big_plan_ref_id = \
                        self._basic_validator.entity_id_validate_and_clean(inbox_task_notion_row.big_plan_ref_id)\
                        if inbox_task_notion_row.big_plan_ref_id else None
                    inbox_task_big_plan_name = \
                        self._basic_validator.entity_name_validate_and_clean(inbox_task_notion_row.big_plan_name)\
                        if inbox_task_notion_row.big_plan_name else None
                    inbox_task_recurring_task_ref_id = \
                        self._basic_validator.entity_id_validate_and_clean(inbox_task_notion_row.recurring_task_ref_id)\
                        if inbox_task_notion_row.recurring_task_ref_id else None
                    inbox_task_status = \
                        self._basic_validator.inbox_task_status_validate_and_clean(inbox_task_notion_row.status)\
                        if inbox_task_notion_row.status else InboxTaskStatus.NOT_STARTED
                    inbox_task_eisen = \
                        [self._basic_validator.eisen_validate_and_clean(e) for e in inbox_task_notion_row.eisen]\
                        if inbox_task_notion_row.eisen else []
                    inbox_task_difficulty = \
                        self._basic_validator.difficulty_validate_and_clean(inbox_task_notion_row.difficulty)\
                        if inbox_task_notion_row.difficulty else None
                    inbox_task_recurring_task_type = \
                        self._basic_validator.recurring_task_type_validate_and_clean(
                            inbox_task_notion_row.recurring_task_type) \
                        if inbox_task_notion_row.recurring_task_type else None
                    self._check_actionable_and_due_dates(
                        inbox_task_notion_row.actionable_date, inbox_task_notion_row.due_date)
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                big_plan = None
                recurring_task = None
                if inbox_task_big_plan_ref_id is not None:
                    big_plan = all_big_plans_map[inbox_task_big_plan_ref_id]
                elif inbox_task_big_plan_name is not None:
                    big_plan = \
                        all_big_plans_by_name[remote.notion.common.format_name_for_option(inbox_task_big_plan_name)]
                elif inbox_task_recurring_task_ref_id is not None:
                    recurring_task = all_recurring_tasks_map[inbox_task_recurring_task_ref_id]

                new_inbox_task_row = self._repository.create_inbox_task(
                    project_ref_id=project_ref_id,
                    big_plan_ref_id=big_plan.ref_id if big_plan else None,
                    recurring_task_ref_id=recurring_task.ref_id if recurring_task else None,
                    name=inbox_task_name,
                    archived=inbox_task_notion_row.archived,
                    status=inbox_task_status,
                    eisen=inbox_task_eisen,
                    difficulty=inbox_task_difficulty,
                    actionable_date=inbox_task_notion_row.actionable_date,
                    due_date=inbox_task_notion_row.due_date,
                    recurring_task_timeline=inbox_task_notion_row.recurring_timeline,
                    recurring_task_type=inbox_task_recurring_task_type,
                    recurring_task_gen_right_now=inbox_task_notion_row.recurring_task_gen_right_now)
                LOGGER.info(f"Found new inbox task from Notion {inbox_task_notion_row.name}")

                self._notion_manager.link_local_and_notion_entries(
                    project_ref_id, new_inbox_task_row.ref_id, inbox_task_notion_row.notion_id)
                LOGGER.info(f"Linked the new inbox task with local entries")

                inbox_task_notion_row.ref_id = new_inbox_task_row.ref_id
                inbox_task_notion_row.status = new_inbox_task_row.status.for_notion()
                inbox_task_notion_row.big_plan_ref_id = big_plan.ref_id if big_plan else None
                inbox_task_notion_row.recurring_task_ref_id = recurring_task.ref_id if recurring_task else None
                self._notion_manager.save_inbox_task(
                    project_ref_id, inbox_task_notion_row.ref_id, inbox_task_notion_row)
                LOGGER.info(f"Applied changes on Notion side too as {inbox_task_notion_row}")

                all_inbox_task_rows_set[inbox_task_notion_row.ref_id] = new_inbox_task_row
                all_inbox_tasks_notion_row_set[inbox_task_notion_row.ref_id] = inbox_task_notion_row
            elif inbox_task_notion_row.ref_id in all_inbox_task_rows_set and \
                    inbox_task_notion_row.notion_id in all_inbox_task_notion_ids:
                # If the big plan exists locally, we sync it with the remote
                inbox_task_row = all_inbox_task_rows_set[EntityId(inbox_task_notion_row.ref_id)]
                all_inbox_tasks_notion_row_set[EntityId(inbox_task_notion_row.ref_id)] = inbox_task_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    # Copy over the parameters from Notion to local
                    if not sync_even_if_not_modified \
                            and inbox_task_notion_row.last_edited_time <= inbox_task_row.last_modified_time:
                        LOGGER.info(f"Skipping {inbox_task_notion_row.name} because it was not modified")
                        continue

                    try:
                        inbox_task_name = \
                            self._basic_validator.entity_name_validate_and_clean(inbox_task_notion_row.name)
                        inbox_task_big_plan_ref_id = \
                            self._basic_validator.entity_id_validate_and_clean(inbox_task_notion_row.big_plan_ref_id) \
                                if inbox_task_notion_row.big_plan_ref_id else None
                        inbox_task_big_plan_name = self._basic_validator.entity_name_validate_and_clean(
                            inbox_task_notion_row.big_plan_name) \
                            if inbox_task_notion_row.big_plan_name else None
                        inbox_task_recurring_task_ref_id = \
                            self._basic_validator.entity_id_validate_and_clean(
                                inbox_task_notion_row.recurring_task_ref_id) \
                                if inbox_task_notion_row.recurring_task_ref_id else None
                        inbox_task_status = \
                            self._basic_validator.inbox_task_status_validate_and_clean(inbox_task_notion_row.status) \
                                if inbox_task_notion_row.status else InboxTaskStatus.NOT_STARTED
                        inbox_task_eisen = \
                            [self._basic_validator.eisen_validate_and_clean(e) for e in inbox_task_notion_row.eisen] \
                                if inbox_task_notion_row.eisen else []
                        inbox_task_difficulty = \
                            self._basic_validator.difficulty_validate_and_clean(inbox_task_notion_row.difficulty) \
                                if inbox_task_notion_row.difficulty else None
                        inbox_task_recurring_task_type = \
                            self._basic_validator.recurring_task_type_validate_and_clean(
                                inbox_task_notion_row.recurring_task_type) \
                            if inbox_task_notion_row.recurring_task_type else None
                        self._check_actionable_and_due_dates(
                            inbox_task_notion_row.actionable_date, inbox_task_notion_row.due_date)
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    big_plan = None
                    recurring_task = None
                    if inbox_task_big_plan_ref_id is not None:
                        big_plan = all_big_plans_map[inbox_task_big_plan_ref_id]
                    elif inbox_task_big_plan_name is not None:
                        big_plan = \
                            all_big_plans_by_name[remote.notion.common.format_name_for_option(inbox_task_big_plan_name)]
                    elif inbox_task_recurring_task_ref_id is not None:
                        recurring_task = all_recurring_tasks_map[inbox_task_recurring_task_ref_id]

                    archived_time_action = \
                        TimeFieldAction.SET if not inbox_task_row.archived and inbox_task_notion_row.archived else \
                        TimeFieldAction.CLEAR if inbox_task_row.archived and not inbox_task_notion_row.archived else \
                        TimeFieldAction.DO_NOTHING
                    accepted_time_action = \
                        TimeFieldAction.SET if \
                            (not inbox_task_row.status.is_accepted_or_more
                             and inbox_task_status.is_accepted_or_more) else \
                        TimeFieldAction.CLEAR if \
                            (inbox_task_row.status.is_accepted_or_more
                             and not inbox_task_status.is_accepted_or_more) else \
                        TimeFieldAction.DO_NOTHING
                    working_time_action = \
                        TimeFieldAction.SET if \
                            (not inbox_task_row.status.is_working_or_more
                             and inbox_task_status.is_working_or_more) else \
                        TimeFieldAction.CLEAR if \
                            (inbox_task_row.status.is_working_or_more
                             and not inbox_task_status.is_working_or_more) else \
                        TimeFieldAction.DO_NOTHING
                    completed_time_action = \
                        TimeFieldAction.SET if \
                            (not inbox_task_row.status.is_completed
                             and inbox_task_status.is_completed) else \
                        TimeFieldAction.CLEAR if \
                            (inbox_task_row.status.is_completed
                             and not inbox_task_status.is_completed) else \
                        TimeFieldAction.DO_NOTHING
                    inbox_task_row.big_plan_ref_id = big_plan.ref_id if big_plan else None
                    if recurring_task is None:
                        inbox_task_row.name = inbox_task_name
                        inbox_task_row.eisen = inbox_task_eisen
                        inbox_task_row.difficulty = inbox_task_difficulty
                    inbox_task_row.archived = inbox_task_notion_row.archived
                    inbox_task_row.status = inbox_task_status
                    inbox_task_row.actionable_date = inbox_task_notion_row.actionable_date
                    inbox_task_row.due_date = inbox_task_notion_row.due_date
                    inbox_task_row.recurring_task_timeline = inbox_task_notion_row.recurring_timeline
                    inbox_task_row.recurring_task_type = inbox_task_recurring_task_type
                    self._repository.update_inbox_task(
                        inbox_task_row, archived_time_action=archived_time_action,
                        accepted_time_action=accepted_time_action, working_time_action=working_time_action,
                        completed_time_action=completed_time_action)
                    LOGGER.info(f"Changed inbox task with id={inbox_task_notion_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            inbox_task_row.last_modified_time <= inbox_task_notion_row.last_edited_time:
                        LOGGER.info(f"Skipping {inbox_task_row.name} because it was not modified")
                        continue

                    big_plan = None
                    recurring_task = None
                    if inbox_task_row.big_plan_ref_id is not None:
                        big_plan = all_big_plans_map[inbox_task_row.big_plan_ref_id]
                    elif inbox_task_row.recurring_task_ref_id is not None:
                        recurring_task = all_recurring_tasks_map[inbox_task_row.recurring_task_ref_id]

                    inbox_task_notion_row.big_plan_ref_id = inbox_task_row.big_plan_ref_id
                    inbox_task_notion_row.big_plan_name = \
                        remote.notion.common.format_name_for_option(big_plan.name) if big_plan else None
                    inbox_task_notion_row.recurring_task_ref_id = inbox_task_row.recurring_task_ref_id
                    inbox_task_notion_row.name = inbox_task_row.name
                    inbox_task_notion_row.archived = inbox_task_row.archived
                    inbox_task_notion_row.status = inbox_task_row.status.for_notion()
                    inbox_task_notion_row.eisen = [e.value for e in inbox_task_row.eisen]
                    inbox_task_notion_row.difficulty = \
                        inbox_task_row.difficulty.value if inbox_task_row.difficulty else None
                    inbox_task_notion_row.actionable_date = inbox_task_row.actionable_date
                    inbox_task_notion_row.due_date = inbox_task_row.due_date
                    inbox_task_notion_row.recurring_timeline = inbox_task_row.recurring_task_timeline
                    inbox_task_notion_row.recurring_period = recurring_task.period.value if recurring_task else None
                    inbox_task_notion_row.recurring_task_type = \
                        recurring_task.the_type.value if recurring_task else None
                    self._notion_manager.save_inbox_task(project_ref_id, inbox_task_row.ref_id, inbox_task_notion_row)
                    LOGGER.info(f"Changed inbox task with id={inbox_task_notion_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random task added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a task added by the script, but which failed before local data could be saved. We'll have
                #    duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_inbox_task(project_ref_id, inbox_task_notion_row.ref_id, )
                LOGGER.info(f"Removed dangling big plan in Notion {inbox_task_notion_row}")

        LOGGER.info("Applied local changes")

        # Now, go over each local recurring task, and add it to Notion if it doesn't
        # exist there!

        for inbox_task_row in all_inbox_task_rows_set.values():
            # We've already processed this thing above
            if inbox_task_row.ref_id in all_inbox_tasks_notion_row_set:
                continue
            if inbox_task_row.archived:
                continue

            big_plan = None
            recurring_task = None
            if inbox_task_row.big_plan_ref_id is not None:
                big_plan = all_big_plans_map[inbox_task_row.big_plan_ref_id]
            elif inbox_task_row.recurring_task_ref_id is not None:
                recurring_task = all_recurring_tasks_map[inbox_task_row.recurring_task_ref_id]

            self._notion_manager.upsert_inbox_task(
                project_ref_id=project_ref_id,
                name=inbox_task_row.name,
                archived=inbox_task_row.archived,
                big_plan_ref_id=big_plan.ref_id if big_plan else None,
                big_plan_name=remote.notion.common.format_name_for_option(
                    big_plan.name) if big_plan else None,
                recurring_task_ref_id=recurring_task.ref_id if recurring_task else None,
                status=inbox_task_row.status.for_notion(),
                eisen=[e.value for e in inbox_task_row.eisen],
                difficulty=inbox_task_row.difficulty.value if inbox_task_row.difficulty else None,
                actionable_date=inbox_task_row.actionable_date,
                due_date=inbox_task_row.due_date,
                recurring_timeline=inbox_task_row.recurring_task_timeline,
                recurring_period=recurring_task.period.value if recurring_task else None,
                recurring_task_type=recurring_task.the_type.value if recurring_task else None,
                recurring_task_gen_right_now=inbox_task_row.recurring_task_gen_right_now,
                ref_id=inbox_task_row.ref_id)
            LOGGER.info(f'Created Notion inbox task for {inbox_task_row.name}')

        return [self._row_to_entity(it) for it in all_inbox_task_rows_set.values()]

    @staticmethod
    def _check_actionable_and_due_dates(actionable_date: Optional[ADate], due_date: Optional[ADate]) -> None:
        if actionable_date is None or due_date is None:
            return

        actionable_date_ts = actionable_date if isinstance(actionable_date, pendulum.DateTime) else \
            pendulum.DateTime(actionable_date.year, actionable_date.month, actionable_date.day, tzinfo=UTC)
        due_date_ts = due_date if isinstance(due_date, pendulum.DateTime) else \
            pendulum.DateTime(due_date.year, due_date.month, due_date.day, tzinfo=UTC)

        if actionable_date_ts > due_date_ts:
            raise ServiceValidationError(
                f"The actionable date {actionable_date} should be before the due date {due_date}")

    @staticmethod
    def _row_to_entity(row: InboxTaskRow) -> InboxTask:
        return InboxTask(
            ref_id=row.ref_id,
            project_ref_id=row.project_ref_id,
            big_plan_ref_id=row.big_plan_ref_id,
            recurring_task_ref_id=row.recurring_task_ref_id,
            archived=row.archived,
            name=row.name,
            status=row.status,
            eisen=row.eisen,
            difficulty=row.difficulty,
            actionable_date=row.actionable_date,
            due_date=row.due_date,
            recurring_task_timeline=row.recurring_task_timeline,
            recurring_task_type=row.recurring_task_type,
            recurring_task_gen_right_now=row.recurring_task_gen_right_now,
            created_time=row.created_time,
            last_modified_time=row.last_modified_time,
            accepted_time=row.accepted_time,
            working_time=row.working_time,
            completed_time=row.completed_time)
