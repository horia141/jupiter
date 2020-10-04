"""The service class for dealing with recurring tasks."""
import logging
from typing import Final, Optional, Iterable, List

from models.basic import EntityId, Difficulty, Eisen, BasicValidator, ModelValidationError, RecurringTaskPeriod, \
    SyncPrefer, RecurringTaskType, ADate
from remote.notion.common import NotionPageLink, NotionCollectionLink, CollectionError, CollectionEntityNotFound
from remote.notion.recurring_tasks import RecurringTasksCollection
from repository.recurring_tasks import RecurringTasksRepository, RecurringTask
from service.errors import ServiceValidationError
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTasksService:
    """The service class for dealing with recurring tasks."""

    _basic_validator: Final[BasicValidator]
    _time_provider: Final[TimeProvider]
    _repository: Final[RecurringTasksRepository]
    _collection: Final[RecurringTasksCollection]

    def __init__(
            self, basic_validator: BasicValidator, time_provider: TimeProvider, repository: RecurringTasksRepository,
            collection: RecurringTasksCollection) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._time_provider = time_provider
        self._repository = repository
        self._collection = collection

    def upsert_notion_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Upsert the Notion-side structure for inbox tasks."""
        return self._collection.upsert_recurring_tasks_structure(project_ref_id, parent_page)

    def remove_notion_structure(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for inbox tasks."""
        for recurring_task in self._repository.load_all_recurring_tasks(filter_project_ref_ids=[project_ref_id]):
            self._repository.archive_recurring_task(recurring_task.ref_id)
        self._collection.remove_recurring_tasks_structure(project_ref_id)

    def create_recurring_task(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink, name: str,
            period: RecurringTaskPeriod, the_type: RecurringTaskType, eisen: List[Eisen],
            difficulty: Optional[Difficulty], due_at_time: Optional[str], due_at_day: Optional[int],
            due_at_month: Optional[int], must_do: bool, skip_rule: Optional[str], start_at_date: Optional[ADate],
            end_at_date: Optional[ADate]) -> RecurringTask:
        """Create a recurring task."""
        today = self._time_provider.get_current_date()
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
            due_at_time = self._basic_validator.recurring_task_due_at_time_validate_and_clean(due_at_time)\
                if due_at_time else None
            due_at_day = self._basic_validator.recurring_task_due_at_day_validate_and_clean(period, due_at_day)\
                if due_at_day else None
            due_at_month = self._basic_validator.recurring_task_due_at_month_validate_and_clean(period, due_at_month)\
                if due_at_month else None

            if start_at_date is not None and end_at_date is not None and start_at_date >= end_at_date:
                raise ServiceValidationError(f"Start date {start_at_date} is after {end_at_date}")
            if start_at_date is None and end_at_date is not None and end_at_date < today:
                raise ServiceValidationError(f"End date {end_at_date} is before {today}")
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        new_recurring_task = self._repository.create_recurring_task(
            project_ref_id=project_ref_id,
            archived=False,
            name=name,
            period=period,
            the_type=the_type,
            eisen=eisen,
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date if start_at_date else today,
            end_at_date=end_at_date,
            suspended=False)
        LOGGER.info("Applied local changes")
        self._collection.create_recurring_task(
            project_ref_id=project_ref_id,
            archived=False,
            inbox_collection_link=inbox_collection_link,
            name=new_recurring_task.name,
            period=new_recurring_task.period.value,
            the_type=new_recurring_task.the_type.value,
            eisen=[e.value for e in new_recurring_task.eisen],
            difficulty=new_recurring_task.difficulty.value if new_recurring_task.difficulty else None,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            skip_rule=skip_rule,
            must_do=must_do,
            start_at_date=new_recurring_task.start_at_date,
            end_at_date=end_at_date,
            suspended=False,
            ref_id=new_recurring_task.ref_id)
        LOGGER.info("Applied Notion changes")

        return new_recurring_task

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Archive a given recurring task."""
        recurring_task = self._repository.archive_recurring_task(ref_id)
        LOGGER.info("Applied local changes")
        try:
            self._collection.archive_recurring_task(recurring_task.project_ref_id, ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because recurring task was not found")

        return recurring_task

    def set_recurring_task_name(self, ref_id: EntityId, name: str) -> RecurringTask:
        """Change the name of a recurring task."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.name = name
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.name = name
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_period(self, ref_id: EntityId, period: RecurringTaskPeriod) -> RecurringTask:
        """Change the period of a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.period = period
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.period = period.value
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_type(self, ref_id: EntityId, the_type: RecurringTaskType) -> RecurringTask:
        """Change the type of a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.the_type = the_type
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.the_type = the_type.value
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_deadlines(
            self, ref_id: EntityId, due_at_time: Optional[str], due_at_day: Optional[int],
            due_at_month: Optional[int]) -> RecurringTask:
        """Change the deadline of a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)

        try:
            due_at_time = self._basic_validator.recurring_task_due_at_time_validate_and_clean(due_at_time)\
                if due_at_time else None
            due_at_day = self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                recurring_task.period, due_at_day)\
                if due_at_day else None
            due_at_month = self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                recurring_task.period, due_at_month)\
                if due_at_month else None
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        recurring_task.due_at_time = due_at_time
        recurring_task.due_at_day = due_at_day
        recurring_task.due_at_month = due_at_month
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.due_at_time = due_at_time
        recurring_task_row.due_at_day = due_at_day
        recurring_task_row.due_at_month = due_at_month
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> RecurringTask:
        """Change the Eisenhower status of a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.eisen = eisen
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.eisen = [e.value for e in eisen]
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> RecurringTask:
        """Change the difficulty of a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.difficulty = difficulty
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.difficulty = difficulty.value if difficulty else None
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_must_do_state(self, ref_id: EntityId, must_do: bool) -> RecurringTask:
        """Change the must do status for a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.must_do = must_do
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.must_do = must_do
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_skip_rule(self, ref_id: EntityId, skip_rule: Optional[str]) -> RecurringTask:
        """Change the skip rule for a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.skip_rule = skip_rule
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.skip_rule = skip_rule
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_active_interval(
            self, ref_id: EntityId, start_at_date: Optional[ADate], end_at_date: Optional[ADate]) -> RecurringTask:
        """Change the active interval for a recurring task."""
        today = self._time_provider.get_current_date()
        if start_at_date is not None and end_at_date is not None and start_at_date >= end_at_date:
            raise ModelValidationError(f"Start date {start_at_date} is after end date {end_at_date}")
        if start_at_date is None and end_at_date is not None and end_at_date < today:
            raise ModelValidationError(f"End date {end_at_date} is before start date {today}")

        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.start_at_date = start_at_date if start_at_date else today
        recurring_task.end_at_date = end_at_date
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.start_at_date = start_at_date if start_at_date else today
        recurring_task_row.end_at_date = end_at_date
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_suspended(self, ref_id: EntityId, suspended: bool) -> RecurringTask:
        """Change the suspended state for a recurring task."""
        recurring_task = self._repository.load_recurring_task(ref_id)
        recurring_task.suspended = suspended
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
        recurring_task_row.suspended = suspended
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def hard_remove_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Hard remove a recurring task."""
        # Apply changes locally
        recurring_task = self._repository.hard_remove_recurring_task(ref_id)
        LOGGER.info("Applied local changes")

        try:
            recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
            self._collection.hard_remove_recurring_task(recurring_task.project_ref_id, recurring_task_row)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping hard removal on Notion side because recurring task could not be found")

        return recurring_task

    def remove_recurring_task_on_notion_side(self, ref_id: EntityId) -> RecurringTask:
        """Remove entries for a recurring task on Notion-side."""
        recurring_task = self._repository.load_recurring_task(ref_id, allow_archived=True)
        try:
            recurring_task_row = self._collection.load_recurring_task(recurring_task.project_ref_id, ref_id)
            self._collection.hard_remove_recurring_task(recurring_task.project_ref_id, recurring_task_row)
            LOGGER.info("Applied Notion changes")
        except CollectionError:
            LOGGER.info("Skipping removal on Notion side because recurring task could not be found")

        return recurring_task

    def load_all_recurring_tasks(
            self, filter_archived: bool = True, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTask]:
        """Retrieve all the recurring tasks."""
        return self._repository.load_all_recurring_tasks(
            filter_archived=filter_archived,
            filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)

    def load_recurring_task_by_id(self, ref_id: EntityId) -> RecurringTask:
        """Retrieve a particular recurring task by it's id."""
        return self._repository.load_recurring_task(ref_id)

    def recurring_tasks_sync(
            self, project_ref_id: EntityId, drop_all_notion_side: bool, inbox_collection_link: NotionCollectionLink,
            sync_even_if_not_modified: bool, filter_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[RecurringTask]:
        """Synchronise recurring tasks between Notion and local storage."""
        today = self._time_provider.get_current_date()
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        # Load local storage
        all_recurring_tasks = self._repository.load_all_recurring_tasks(
            filter_archived=False, filter_ref_ids=filter_ref_ids, filter_project_ref_ids=[project_ref_id])
        all_recurring_tasks_set = {rt.ref_id: rt for rt in all_recurring_tasks}

        if not drop_all_notion_side:
            all_recurring_tasks_rows = self._collection.load_all_recurring_tasks(project_ref_id)
            all_recurring_tasks_saved_notion_ids = \
                set(self._collection.load_all_saved_recurring_tasks_notion_ids(project_ref_id))
        else:
            self._collection.drop_all_recurring_tasks(project_ref_id)
            all_recurring_tasks_rows = {}
            all_recurring_tasks_saved_notion_ids = set()
        all_recurring_tasks_row_set = {}

        # Then look at each recurring task in Notion and try to match it with one in the local storage

        for recurring_task_row in all_recurring_tasks_rows:
            # Skip this step when asking only for particular entities to be synced.
            if filter_ref_ids_set is not None and recurring_task_row.ref_id not in filter_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{recurring_task_row.name}' (id={recurring_task_row.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Syncing '{recurring_task_row.name}' (id={recurring_task_row.notion_id})")

            if recurring_task_row.ref_id is None or recurring_task_row.ref_id == "":
                # If the recurring task doesn't exist locally, we create it!

                try:
                    recurring_task_name = self._basic_validator.entity_name_validate_and_clean(
                        recurring_task_row.name)
                    recurring_task_period = self._basic_validator.recurring_task_period_validate_and_clean(
                        recurring_task_row.period)
                    recurring_task_type = self._basic_validator.recurring_task_type_validate_and_clean(
                        recurring_task_row.the_type) if recurring_task_row.the_type else RecurringTaskType.CHORE
                    recurring_task_eisen = \
                        [self._basic_validator.eisen_validate_and_clean(e) for e in recurring_task_row.eisen] \
                            if recurring_task_row.eisen else []
                    recurring_task_difficulty = \
                        self._basic_validator.difficulty_validate_and_clean(recurring_task_row.difficulty) \
                            if recurring_task_row.difficulty else None
                    recurring_task_due_at_time = \
                        self._basic_validator.recurring_task_due_at_time_validate_and_clean(
                            recurring_task_row.due_at_time) \
                            if recurring_task_row.due_at_time else None
                    recurring_task_due_at_day = \
                        self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                            recurring_task_period, recurring_task_row.due_at_day) \
                            if recurring_task_row.due_at_day else None
                    recurring_task_due_at_month = \
                        self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                            recurring_task_period, recurring_task_row.due_at_month) \
                            if recurring_task_row.due_at_month else None

                    if recurring_task_row.start_at_date is not None and recurring_task_row.end_at_date is not None \
                            and recurring_task_row.start_at_date >= recurring_task_row.end_at_date:
                        raise ModelValidationError(
                            f"Start date {recurring_task_row.start_at_date} is after " +
                            "end date {recurring_task_row.end_at_date}")
                    if recurring_task_row.start_at_date is None and recurring_task_row.end_at_date is not None \
                            and recurring_task_row.end_at_date < today:
                        raise ModelValidationError(
                            f"End date {recurring_task_row.end_at_date} is before start date {today}")
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                new_recurring_task = self._repository.create_recurring_task(
                    project_ref_id=project_ref_id,
                    archived=recurring_task_row.archived,
                    name=recurring_task_name,
                    period=recurring_task_period,
                    the_type=recurring_task_type,
                    eisen=recurring_task_eisen,
                    difficulty=recurring_task_difficulty,
                    due_at_time=recurring_task_due_at_time,
                    due_at_day=recurring_task_due_at_day,
                    due_at_month=recurring_task_due_at_month,
                    suspended=recurring_task_row.suspended,
                    skip_rule=recurring_task_row.skip_rule,
                    must_do=recurring_task_row.must_do,
                    start_at_date=recurring_task_row.start_at_date if recurring_task_row.start_at_date else today,
                    end_at_date=recurring_task_row.end_at_date)
                LOGGER.info(f"Found new recurring task from Notion {recurring_task_row.name}")

                self._collection.link_local_and_notion_entries(
                    project_ref_id, new_recurring_task.ref_id, recurring_task_row.notion_id)
                LOGGER.info(f"Linked the new inbox task with local entries")

                recurring_task_row.ref_id = new_recurring_task.ref_id
                recurring_task_row.start_at_date = new_recurring_task.start_at_date
                self._collection.save_recurring_task(
                    project_ref_id, recurring_task_row, inbox_collection_link=inbox_collection_link)
                LOGGER.info(f"Applies changes on Notion side too as {recurring_task_row}")

                all_recurring_tasks_set[recurring_task_row.ref_id] = new_recurring_task
                all_recurring_tasks_row_set[recurring_task_row.ref_id] = recurring_task_row
            elif recurring_task_row.ref_id in all_recurring_tasks_set \
                    and recurring_task_row.notion_id in all_recurring_tasks_saved_notion_ids:
                # If the recurring task exists locally, we sync it with the remote
                recurring_task = all_recurring_tasks_set[EntityId(recurring_task_row.ref_id)]
                all_recurring_tasks_row_set[EntityId(recurring_task_row.ref_id)] = recurring_task_row

                if sync_prefer == SyncPrefer.NOTION:
                    # Copy over the parameters from Notion to local
                    if not sync_even_if_not_modified \
                            and recurring_task_row.last_edited_time <= recurring_task.last_modified_time:
                        LOGGER.info(f"Skipping {recurring_task_row.name} because it was not modified")
                        continue

                    try:
                        recurring_task_name = self._basic_validator.entity_name_validate_and_clean(
                            recurring_task_row.name)
                        recurring_task_period = self._basic_validator.recurring_task_period_validate_and_clean(
                            recurring_task_row.period)
                        recurring_task_type = self._basic_validator.recurring_task_type_validate_and_clean(
                            recurring_task_row.the_type) if recurring_task_row.the_type else RecurringTaskType.CHORE
                        recurring_task_eisen = \
                            [self._basic_validator.eisen_validate_and_clean(e) for e in recurring_task_row.eisen] \
                                if recurring_task_row.eisen else []
                        recurring_task_difficulty = \
                            self._basic_validator.difficulty_validate_and_clean(recurring_task_row.difficulty) \
                                if recurring_task_row.difficulty else None
                        recurring_task_due_at_time = \
                            self._basic_validator.recurring_task_due_at_time_validate_and_clean(
                                recurring_task_row.due_at_time) \
                                if recurring_task_row.due_at_time else None
                        recurring_task_due_at_day = \
                            self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                                recurring_task_period, recurring_task_row.due_at_day) \
                                if recurring_task_row.due_at_day else None
                        recurring_task_due_at_month = \
                            self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                                recurring_task_period, recurring_task_row.due_at_month) \
                                if recurring_task_row.due_at_month else None

                        if recurring_task_row.start_at_date is not None and recurring_task_row.end_at_date is not None \
                                and recurring_task_row.start_at_date >= recurring_task_row.end_at_date:
                            raise ModelValidationError(
                                f"Start date {recurring_task_row.start_at_date} is after " +
                                "end date {recurring_task_row.end_at_date}")
                        if recurring_task_row.start_at_date is None and recurring_task_row.end_at_date is not None \
                                and recurring_task_row.end_at_date < today:
                            raise ModelValidationError(
                                f"End date {recurring_task_row.end_at_date} is before start date {today}")
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    archived_time_action = \
                        TimeFieldAction.SET if not recurring_task.archived and recurring_task_row.archived else \
                        TimeFieldAction.CLEAR if recurring_task.archived and not recurring_task_row.archived else \
                        TimeFieldAction.DO_NOTHING
                    recurring_task.name = recurring_task_name
                    recurring_task.period = recurring_task_period
                    recurring_task.the_type = recurring_task_type
                    recurring_task.archived = recurring_task_row.archived
                    recurring_task.eisen = recurring_task_eisen
                    recurring_task.difficulty = recurring_task_difficulty
                    recurring_task.due_at_time = recurring_task_due_at_time
                    recurring_task.due_at_day = recurring_task_due_at_day
                    recurring_task.due_at_month = recurring_task_due_at_month
                    recurring_task.suspended = recurring_task_row.suspended
                    recurring_task.skip_rule = recurring_task_row.skip_rule
                    recurring_task.must_do = recurring_task_row.must_do
                    recurring_task.start_at_date = \
                        recurring_task_row.start_at_date if recurring_task_row.start_at_date else today
                    recurring_task.end_at_date = recurring_task_row.end_at_date
                    self._repository.save_recurring_task(recurring_task, archived_time_action=archived_time_action)
                    LOGGER.info(f"Changed recurring task with id={recurring_task_row.ref_id} from Notion")

                    if recurring_task_row.start_at_date is None:
                        recurring_task_row.start_at_date = recurring_task.start_at_date
                        self._collection.save_recurring_task(
                            project_ref_id, recurring_task_row, inbox_collection_link=inbox_collection_link)
                        LOGGER.info(f"Applies changes on Notion side too as {recurring_task_row}")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    if not sync_even_if_not_modified and\
                            recurring_task.last_modified_time <= recurring_task_row.last_edited_time:
                        LOGGER.info(f"Skipping {recurring_task.name} because it was not modified")
                        continue

                    recurring_task_row.name = recurring_task.name
                    recurring_task_row.period = recurring_task.period.value
                    recurring_task_row.the_type = recurring_task.the_type.value
                    recurring_task_row.archived = recurring_task.archived
                    recurring_task_row.eisen = [e.value for e in recurring_task.eisen]
                    recurring_task_row.difficulty = \
                        recurring_task.difficulty.value if recurring_task.difficulty else None
                    recurring_task_row.due_at_time = recurring_task.due_at_time
                    recurring_task_row.due_at_day = recurring_task.due_at_day
                    recurring_task_row.due_at_month = recurring_task.due_at_month
                    recurring_task_row.must_do = recurring_task.must_do
                    recurring_task_row.skip_rule = recurring_task.skip_rule
                    recurring_task_row.start_at_date = recurring_task.start_at_date
                    recurring_task_row.end_at_date = recurring_task.end_at_date
                    self._collection.save_recurring_task(
                        project_ref_id, recurring_task_row, inbox_collection_link=inbox_collection_link)
                    LOGGER.info(f"Changed recurring task with id={recurring_task_row.ref_id} from local")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random task added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a task added by the script, but which failed before local data could be saved. We'll have
                #    duplicates in these cases, and they need to be removed.
                LOGGER.info(f"Removed dangling recurring task in Notion {recurring_task_row}")
                self._collection.hard_remove_recurring_task(project_ref_id, recurring_task_row)

        LOGGER.info("Applied local changes")

        # Now, go over each local recurring task, and add it to Notion if it doesn't
        # exist there!

        for recurring_task in all_recurring_tasks_set.values():
            # We've already processed this thing above
            if recurring_task.ref_id in all_recurring_tasks_row_set:
                continue
            if recurring_task.archived:
                continue

            self._collection.create_recurring_task(
                project_ref_id=project_ref_id,
                archived=recurring_task.archived,
                inbox_collection_link=inbox_collection_link,
                name=recurring_task.name,
                period=recurring_task.period.value,
                the_type=recurring_task.the_type.value,
                eisen=[e.value for e in recurring_task.eisen],
                difficulty=recurring_task.difficulty.value if recurring_task.difficulty else None,
                due_at_time=recurring_task.due_at_time,
                due_at_day=recurring_task.due_at_day,
                due_at_month=recurring_task.due_at_month,
                skip_rule=recurring_task.skip_rule,
                must_do=recurring_task.must_do,
                start_at_date=recurring_task.start_at_date,
                end_at_date=recurring_task.end_at_date,
                suspended=recurring_task.suspended,
                ref_id=recurring_task.ref_id)
            LOGGER.info(f'Created Notion task for {recurring_task.name}')

        return all_recurring_tasks_set.values()
