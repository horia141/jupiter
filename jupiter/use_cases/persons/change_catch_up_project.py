"""Update the persons catch up project."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, cast

from jupiter.domain.adate import ADate
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonChangeCatchUpProjectUseCase(AppMutationUseCase['PersonChangeCatchUpProjectUseCase.Args', None]):
    """The command for updating the catch up project for persons."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        catch_up_project_key: Optional[ProjectKey]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _person_notion_manager: Final[PersonNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            person_notion_manager: PersonNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._person_notion_manager = person_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(workspace.ref_id)

            person_collection = uow.person_collection_repository.load_by_parent(workspace.ref_id)
            old_catch_up_project_ref_id = person_collection.catch_up_project_ref_id

            if args.catch_up_project_key is not None:
                project = uow.project_repository.load_by_key(project_collection.ref_id, args.catch_up_project_key)
                catch_up_project_ref_id = project.ref_id
            else:
                catch_up_project_ref_id = workspace.default_project_ref_id

            person_collection =\
                person_collection.change_catch_up_project(
                    catch_up_project_ref_id=catch_up_project_ref_id, source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time())

            uow.person_collection_repository.save(person_collection)

            persons = \
                uow.person_repository.find_all(parent_ref_id=person_collection.ref_id, allow_archived=False)
            persons_by_ref_id = {p.ref_id: p for p in persons}

        if old_catch_up_project_ref_id != catch_up_project_ref_id and len(persons) > 0:
            LOGGER.info("Moving all inbox tasks too")
            with self._storage_engine.get_unit_of_work() as inbox_task_uow:
                inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(workspace.ref_id)
                all_catch_up_inbox_tasks = \
                    inbox_task_uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                        filter_person_ref_ids=[p.ref_id for p in persons])
                for inbox_task in all_catch_up_inbox_tasks:
                    inbox_task.update_link_to_person_catch_up(
                        project_ref_id=catch_up_project_ref_id,
                        name=inbox_task.name,
                        recurring_timeline=cast(str, inbox_task.recurring_timeline),
                        eisen=inbox_task.eisen,
                        difficulty=inbox_task.difficulty,
                        actionable_date=inbox_task.actionable_date,
                        due_time=cast(ADate, inbox_task.due_date),
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time())
                    uow.inbox_task_repository.save(inbox_task)
                all_birthday_inbox_tasks = \
                    inbox_task_uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                        filter_person_ref_ids=[p.ref_id for p in persons])
                for inbox_task in all_birthday_inbox_tasks:
                    person = persons_by_ref_id[cast(EntityId, inbox_task.person_ref_id)]
                    inbox_task.update_link_to_person_birthday(
                        project_ref_id=catch_up_project_ref_id,
                        name=inbox_task.name,
                        recurring_timeline=cast(str, inbox_task.recurring_timeline),
                        preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                        due_time=cast(ADate, inbox_task.due_date),
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time())
                    uow.inbox_task_repository.save(inbox_task)
