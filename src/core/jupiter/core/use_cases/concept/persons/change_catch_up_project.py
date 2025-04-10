"""Update the persons catch up project."""

from typing import cast

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class PersonChangeCatchUpProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    catch_up_project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.PERSONS, WorkspaceFeature.PROJECTS])
class PersonChangeCatchUpProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonChangeCatchUpProjectArgs, None],
):
    """The command for updating the catch up project for persons."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: PersonChangeCatchUpProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        old_catch_up_project_ref_id = person_collection.catch_up_project_ref_id

        await uow.get_for(Project).load_by_id(
            args.catch_up_project_ref_id,
        )

        persons = await uow.get_for(Person).find_all(
            parent_ref_id=person_collection.ref_id,
            allow_archived=False,
        )
        persons_by_ref_id = {p.ref_id: p for p in persons}

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        all_catch_up_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=[InboxTaskSource.PERSON_CATCH_UP],
            source_entity_ref_id=[p.ref_id for p in persons],
        )
        all_birthday_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=[InboxTaskSource.PERSON_BIRTHDAY],
            source_entity_ref_id=[p.ref_id for p in persons],
        )

        if (
            old_catch_up_project_ref_id != args.catch_up_project_ref_id
            and len(persons) > 0
        ):
            for inbox_task in all_catch_up_inbox_tasks:
                inbox_task = inbox_task.update_link_to_person_catch_up(
                    ctx=context.domain_context,
                    project_ref_id=args.catch_up_project_ref_id,
                    name=inbox_task.name,
                    recurring_timeline=cast(str, inbox_task.recurring_timeline),
                    eisen=inbox_task.eisen,
                    difficulty=inbox_task.difficulty,
                    actionable_date=inbox_task.actionable_date,
                    due_time=cast(ADate, inbox_task.due_date),
                )

                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

            for inbox_task in all_birthday_inbox_tasks:
                person = persons_by_ref_id[inbox_task.source_entity_ref_id_for_sure]
                inbox_task = inbox_task.update_link_to_person_birthday(
                    ctx=context.domain_context,
                    project_ref_id=args.catch_up_project_ref_id,
                    name=inbox_task.name,
                    recurring_timeline=cast(str, inbox_task.recurring_timeline),
                    preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                    due_time=cast(ADate, inbox_task.due_date),
                )

                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

        person_collection = person_collection.change_catch_up_project(
            ctx=context.domain_context,
            catch_up_project_ref_id=args.catch_up_project_ref_id,
        )

        await uow.get_for(PersonCollection).save(person_collection)
