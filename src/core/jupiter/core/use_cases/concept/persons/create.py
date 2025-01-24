"""Create a person."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.persons.person_birthday import PersonBirthday
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.persons.person_name import PersonName
from jupiter.core.domain.concept.persons.person_relationship import PersonRelationship
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class PersonCreateArgs(UseCaseArgsBase):
    """Person create args.."""

    name: PersonName
    relationship: PersonRelationship
    catch_up_period: RecurringTaskPeriod | None
    catch_up_eisen: Eisen | None
    catch_up_difficulty: Difficulty | None
    catch_up_actionable_from_day: RecurringTaskDueAtDay | None
    catch_up_actionable_from_month: RecurringTaskDueAtMonth | None
    catch_up_due_at_day: RecurringTaskDueAtDay | None
    catch_up_due_at_month: RecurringTaskDueAtMonth | None
    birthday: PersonBirthday | None


@use_case_result
class PersonCreateResult(UseCaseResultBase):
    """Person create result."""

    new_person: Person


@mutation_use_case(WorkspaceFeature.PERSONS)
class PersonCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonCreateArgs, PersonCreateResult]
):
    """The command for creating a person."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: PersonCreateArgs,
    ) -> PersonCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )

        catch_up_params = None
        if args.catch_up_period is not None:
            catch_up_params = RecurringTaskGenParams(
                period=args.catch_up_period,
                eisen=args.catch_up_eisen,
                difficulty=args.catch_up_difficulty,
                actionable_from_day=args.catch_up_actionable_from_day,
                actionable_from_month=args.catch_up_actionable_from_month,
                due_at_day=args.catch_up_due_at_day,
                due_at_month=args.catch_up_due_at_month,
            )

        new_person = Person.new_person(
            ctx=context.domain_context,
            person_collection_ref_id=person_collection.ref_id,
            name=args.name,
            relationship=args.relationship,
            catch_up_params=catch_up_params,
            birthday=args.birthday,
        )
        new_person = await uow.get_for(Person).create(new_person)
        await progress_reporter.mark_created(new_person)

        return PersonCreateResult(new_person=new_person)

    async def _perform_post_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: PersonCreateArgs,
        result: PersonCreateResult,
    ) -> None:
        """Execute the command's post-mutation work."""
        await GenService(self._domain_storage_engine).do_it(
            context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=False,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.PERSONS],
            period=[args.catch_up_period] if args.catch_up_period else [],
            filter_person_ref_ids=[result.new_person.ref_id],
        )
