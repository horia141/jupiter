"""The service class for dealing with recurring tasks."""
import logging
from typing import Final, Optional, Iterable, List

from models.basic import EntityId, Difficulty, Eisen, BasicValidator, ModelValidationError, RecurringTaskPeriod, \
    EntityName, SyncPrefer
from remote.notion.common import NotionPageLink, NotionCollectionLink
from remote.notion.recurring_tasks import RecurringTasksCollection
from repository.recurring_tasks import RecurringTasksRepository, RecurringTask
from service.errors import ServiceValidationError

LOGGER = logging.getLogger(__name__)


class RecurringTasksService:
    """The service class for dealing with recurring tasks."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[RecurringTasksRepository]
    _collection: Final[RecurringTasksCollection]

    def __init__(
            self, basic_validator: BasicValidator, repository: RecurringTasksRepository,
            collection: RecurringTasksCollection) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._collection = collection

    def upsert_notion_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Upsert the Notion-side structure for inbox tasks."""
        return self._collection.upsert_recurring_tasks_structure(project_ref_id, parent_page)

    def remove_notion_structure(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for inbox tasks."""
        for recurring_task in self._repository.list_all_recurring_tasks(filter_project_ref_ids=[project_ref_id]):
            self._repository.remove_recurring_task_by_id(recurring_task.ref_id)
        self._collection.remove_recurring_tasks_structure(project_ref_id)

    def create_recurring_task(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink, name: str,
            period: RecurringTaskPeriod, group: EntityName, eisen: List[Eisen], difficulty: Optional[Difficulty],
            due_at_time: Optional[str], due_at_day: Optional[int], due_at_month: Optional[int], must_do: bool,
            skip_rule: Optional[str]) -> RecurringTask:
        """Create a recurring task."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
            due_at_time = self._basic_validator.recurring_task_due_at_time_validate_and_clean(due_at_time)\
                if due_at_time else None
            due_at_day = self._basic_validator.recurring_task_due_at_day_validate_and_clean(period, due_at_day)\
                if due_at_day else None
            due_at_month = self._basic_validator.recurring_task_due_at_month_validate_and_clean(period, due_at_month)\
                if due_at_month else None
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        new_recurring_task = self._repository.create_recurring_task(
            project_ref_id=project_ref_id,
            archived=False,
            name=name,
            period=period,
            group=group,
            eisen=eisen,
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule,
            suspended=False)
        LOGGER.info("Applied local changes")
        self._collection.create_recurring_task(
            project_ref_id=project_ref_id,
            inbox_collection_link=inbox_collection_link,
            name=new_recurring_task.name,
            period=new_recurring_task.period.value,
            group=new_recurring_task.group,
            eisen=[e.value for e in new_recurring_task.eisen],
            difficulty=new_recurring_task.difficulty.value if new_recurring_task.difficulty else None,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule,
            suspended=False,
            ref_id=new_recurring_task.ref_id)
        LOGGER.info("Applied Notion changes")

        return new_recurring_task

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Archive a given recurring task."""
        recurring_task = self._repository.remove_recurring_task_by_id(ref_id)
        LOGGER.info("Applied local changes")
        self._collection.remove_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_name(self, ref_id: EntityId, name: str) -> RecurringTask:
        """Change the name of a recurring task."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.name = name
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.name = name
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_period(self, ref_id: EntityId, period: RecurringTaskPeriod) -> RecurringTask:
        """Change the period of a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.period = period
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.period = period.value
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_deadlines(
            self, ref_id: EntityId, due_at_time: Optional[str], due_at_day: Optional[int],
            due_at_month: Optional[int]) -> RecurringTask:
        """Change the deadline of a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)

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

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.due_at_time = due_at_time
        recurring_task_row.due_at_day = due_at_day
        recurring_task_row.due_at_month = due_at_month
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> RecurringTask:
        """Change the Eisenhower status of a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.eisen = eisen
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.eisen = [e.value for e in eisen]
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> RecurringTask:
        """Change the difficulty of a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.difficulty = difficulty
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.difficulty = difficulty.value if difficulty else None
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

        return recurring_task

    def set_recurring_task_group(self, ref_id: EntityId, group: EntityName) -> None:
        """Change the group for a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.group = group
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.group = group
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

    def set_recurring_task_must_do_state(self, ref_id: EntityId, must_do: bool) -> None:
        """Change the must do status for a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.must_do = must_do
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.must_do = must_do
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

    def set_recurring_task_skip_rule(self, ref_id: EntityId, skip_rule: Optional[str]) -> None:
        """Change the skip rule for a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.skip_rule = skip_rule
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.skip_rule = skip_rule
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

    def set_recurring_task_suspended(self, ref_id: EntityId, suspended: bool) -> None:
        """Change the suspended state for a recurring task."""
        recurring_task = self._repository.load_recurring_task_by_id(ref_id)
        recurring_task.suspended = suspended
        self._repository.save_recurring_task(recurring_task)
        LOGGER.info("Applied local changes")

        recurring_task_row = self._collection.load_recurring_task_by_id(recurring_task.project_ref_id, ref_id)
        recurring_task_row.suspended = suspended
        self._collection.save_recurring_task(recurring_task.project_ref_id, recurring_task_row)
        LOGGER.info("Applied Notion changes")

    def load_all_recurring_tasks(
            self, filter_archived: bool = True, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTask]:
        """Retrieve all the recurring tasks."""
        return self._repository.list_all_recurring_tasks(
            filter_archived=filter_archived,
            filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)

    def load_recurring_task_by_id(self, ref_id: EntityId) -> RecurringTask:
        """Retrieve a particular recurring task by it's id."""
        return self._repository.load_recurring_task_by_id(ref_id)

    def recurring_tasks_sync(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink,
            sync_prefer: SyncPrefer) -> None:
        """Synchronise recurring tasks between Notion and local storage."""
        # Load local storage
        all_recurring_tasks = self._repository.list_all_recurring_tasks(
            filter_archived=False, filter_project_ref_ids=[project_ref_id])
        all_recurring_tasks_set = {rt.ref_id: rt for rt in all_recurring_tasks}
        all_recurring_tasks_rows = self._collection.load_all_recurring_tasks(project_ref_id)
        all_recurring_tasks_row_set = {}

        # Then look at each recurring task in Notion and try to match it with one in the local storage

        for recurring_task_row in all_recurring_tasks_rows:
            LOGGER.info(f"Processing {recurring_task_row}")

            if recurring_task_row.ref_id is None or recurring_task_row.ref_id == "":
                # If the recurring task doesn't exist locally, we create it!

                try:
                    recurring_task_name = self._basic_validator.entity_name_validate_and_clean(
                        recurring_task_row.name)
                    recurring_task_period = self._basic_validator.recurring_task_period_validate_and_clean(
                        recurring_task_row.period)
                    recurring_task_group = self._basic_validator.entity_name_validate_and_clean(
                        recurring_task_row.group)
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
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                new_recurring_task = self._repository.create_recurring_task(
                    project_ref_id=project_ref_id,
                    archived=False,
                    name=recurring_task_name,
                    period=recurring_task_period,
                    group=recurring_task_group,
                    eisen=recurring_task_eisen,
                    difficulty=recurring_task_difficulty,
                    due_at_time=recurring_task_due_at_time,
                    due_at_day=recurring_task_due_at_day,
                    due_at_month=recurring_task_due_at_month,
                    suspended=recurring_task_row.suspended,
                    skip_rule=recurring_task_row.skip_rule,
                    must_do=recurring_task_row.must_do)
                LOGGER.info(f"Found new recurring task from Notion {recurring_task_row.name}")

                self._collection.link_local_and_notion_entries(
                    project_ref_id, new_recurring_task.ref_id, recurring_task_row.notion_id)
                LOGGER.info(f"Linked the new inbox task with local entries")

                recurring_task_row.ref_id = new_recurring_task.ref_id
                self._collection.save_recurring_task(
                    project_ref_id, recurring_task_row, inbox_collection_link=inbox_collection_link)
                LOGGER.info(f"Applies changes on Notion side too as {recurring_task_row}")

                all_recurring_tasks_set[recurring_task_row.ref_id] = new_recurring_task
                all_recurring_tasks_row_set[recurring_task_row.ref_id] = recurring_task_row
            elif recurring_task_row.ref_id in all_recurring_tasks_set:
                # If the recurring task exists locally, we sync it with the remote
                recurring_task = all_recurring_tasks_set[recurring_task_row.ref_id]
                if sync_prefer == SyncPrefer.NOTION:
                    # Copy over the parameters from Notion to local
                    try:
                        recurring_task_name = self._basic_validator.entity_name_validate_and_clean(
                            recurring_task_row.name)
                        recurring_task_period = self._basic_validator.recurring_task_period_validate_and_clean(
                            recurring_task_row.period)
                        recurring_task_group = self._basic_validator.entity_name_validate_and_clean(
                            recurring_task_row.group)
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
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    recurring_task.name = recurring_task_name
                    recurring_task.period = recurring_task_period
                    recurring_task.group = recurring_task_group
                    recurring_task.eisen = recurring_task_eisen
                    recurring_task.difficulty = recurring_task_difficulty
                    recurring_task.due_at_time = recurring_task_due_at_time
                    recurring_task.due_at_day = recurring_task_due_at_day
                    recurring_task.due_at_month = recurring_task_due_at_month
                    recurring_task.suspended = recurring_task_row.suspended
                    recurring_task.skip_rule = recurring_task_row.skip_rule
                    recurring_task.must_do = recurring_task_row.must_do
                    self._repository.save_recurring_task(recurring_task)
                    LOGGER.info(f"Changed recurring task with id={recurring_task_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    # Copy over the parameters from local to Notion
                    recurring_task_row.name = recurring_task.name
                    recurring_task_row.period = recurring_task.period.value
                    recurring_task_row.group = recurring_task.group
                    recurring_task_row.eisen = [e.value for e in recurring_task.eisen]
                    recurring_task_row.difficulty = \
                        recurring_task.difficulty.value if recurring_task.difficulty else None
                    recurring_task_row.due_at_time = recurring_task.due_at_time
                    recurring_task_row.due_at_day = recurring_task.due_at_day
                    recurring_task_row.due_at_month = recurring_task.due_at_month
                    recurring_task_row.must_do = recurring_task.must_do
                    recurring_task_row.skip_rule = recurring_task.skip_rule
                    self._collection.save_recurring_task(
                        project_ref_id, recurring_task_row, inbox_collection_link=inbox_collection_link)
                    LOGGER.info(f"Changed recurring task with id={recurring_task_row.ref_id} from local")
                all_recurring_tasks_row_set[recurring_task_row.ref_id] = recurring_task_row
            else:
                LOGGER.info(f"Removed dangling recurring task in Notion {recurring_task_row}")
                self._collection.hard_remove_recurring_task(project_ref_id, recurring_task_row.ref_id)

        LOGGER.info("Applied local changes")

        # Now, go over each local recurring task, and add it to Notion if it doesn't
        # exist there!

        for recurring_task in all_recurring_tasks_set.values():
            # We've already processed this thing above
            if recurring_task.ref_id in all_recurring_tasks_row_set:
                continue

            self._collection.create_recurring_task(
                project_ref_id=project_ref_id,
                inbox_collection_link=inbox_collection_link,
                name=recurring_task.name,
                period=recurring_task.period.value,
                group=recurring_task.group,
                eisen=[e.value for e in recurring_task.eisen],
                difficulty=recurring_task.difficulty.value,
                due_at_time=recurring_task.due_at_time,
                due_at_day=recurring_task.due_at_day,
                due_at_month=recurring_task.due_at_month,
                must_do=recurring_task.must_do,
                skip_rule=recurring_task.skip_rule,
                suspended=recurring_task.suspended,
                ref_id=recurring_task.ref_id)
            LOGGER.info(f'Created Notion task for {recurring_task.name}')
