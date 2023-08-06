"""Update the persons catch up project."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class PersonChangeCatchUpProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    catch_up_project_ref_id: Optional[EntityId] = None


class PersonChangeCatchUpProjectUseCase(
    AppLoggedInMutationUseCase[PersonChangeCatchUpProjectArgs, None],
):
    """The command for updating the catch up project for persons."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return (Feature.PERSONS, Feature.PROJECTS)

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: PersonChangeCatchUpProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )

            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            old_catch_up_project_ref_id = person_collection.catch_up_project_ref_id

            if args.catch_up_project_ref_id is not None:
                catch_up_project = await uow.project_repository.load_by_id(
                    args.catch_up_project_ref_id,
                )
                catch_up_project_ref_id = catch_up_project.ref_id
            else:
                catch_up_project = await uow.project_repository.load_by_id(
                    workspace.default_project_ref_id,
                )
                catch_up_project_ref_id = workspace.default_project_ref_id

            persons = await uow.person_repository.find_all(
                parent_ref_id=person_collection.ref_id,
                allow_archived=False,
            )
            persons_by_ref_id = {p.ref_id: p for p in persons}

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_catch_up_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                    filter_person_ref_ids=[p.ref_id for p in persons],
                )
            )
            all_birthday_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                    filter_person_ref_ids=[p.ref_id for p in persons],
                )
            )

        if old_catch_up_project_ref_id != catch_up_project_ref_id and len(persons) > 0:
            for inbox_task in all_catch_up_inbox_tasks:
                async with progress_reporter.start_updating_entity(
                    "inbox task",
                    inbox_task.ref_id,
                    str(inbox_task.name),
                ) as entity_reporter:
                    async with self._domain_storage_engine.get_unit_of_work() as uow:
                        inbox_task = inbox_task.update_link_to_person_catch_up(
                            project_ref_id=catch_up_project_ref_id,
                            name=inbox_task.name,
                            recurring_timeline=cast(str, inbox_task.recurring_timeline),
                            eisen=inbox_task.eisen,
                            difficulty=inbox_task.difficulty,
                            actionable_date=inbox_task.actionable_date,
                            due_time=cast(ADate, inbox_task.due_date),
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                        await entity_reporter.mark_known_name(str(inbox_task.name))

                        await uow.inbox_task_repository.save(inbox_task)
                        await entity_reporter.mark_local_change()

            for inbox_task in all_birthday_inbox_tasks:
                async with progress_reporter.start_updating_entity(
                    "inbox task",
                    inbox_task.ref_id,
                    str(inbox_task.name),
                ) as entity_reporter:
                    async with self._domain_storage_engine.get_unit_of_work() as uow:
                        person = persons_by_ref_id[
                            cast(EntityId, inbox_task.person_ref_id)
                        ]
                        inbox_task = inbox_task.update_link_to_person_birthday(
                            project_ref_id=catch_up_project_ref_id,
                            name=inbox_task.name,
                            recurring_timeline=cast(str, inbox_task.recurring_timeline),
                            preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                            due_time=cast(ADate, inbox_task.due_date),
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                        await entity_reporter.mark_known_name(str(inbox_task.name))

                        await uow.inbox_task_repository.save(inbox_task)
                        await entity_reporter.mark_local_change()

        async with progress_reporter.start_updating_entity(
            "person collection",
            person_collection.ref_id,
            "Person Collection",
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                person_collection = person_collection.change_catch_up_project(
                    catch_up_project_ref_id=catch_up_project_ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                await uow.person_collection_repository.save(person_collection)
                await entity_reporter.mark_local_change()
