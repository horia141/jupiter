"""Use case for creating a time plan."""

from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class TimePlanCreateArgs(UseCaseArgsBase):
    """Args."""

    today: ADate
    period: RecurringTaskPeriod


@use_case_result
class TimePlanCreateResult(UseCaseResultBase):
    """Result."""

    new_time_plan: TimePlan
    new_note: Note


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[TimePlanCreateArgs, TimePlanCreateResult]
):
    """Use case for creating a time plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanCreateArgs,
    ) -> TimePlanCreateResult:
        """Execute the command's actions."""
        workspace = context.workspace

        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id,
        )
        note_collection = await uow.get_for(NoteCollection).load_by_parent(
            workspace.ref_id
        )

        new_time_plan = TimePlan.new_time_plan_for_user(
            context.domain_context,
            time_plan_domain_ref_id=time_plan_domain.ref_id,
            today=args.today,
            period=args.period,
        )
        new_time_plan = await generic_creator(uow, progress_reporter, new_time_plan)

        new_note = Note.new_note(
            context.domain_context,
            note_collection_ref_id=note_collection.ref_id,
            domain=NoteDomain.TIME_PLAN,
            source_entity_ref_id=new_time_plan.ref_id,
            content=[],
        )
        new_note = await generic_creator(uow, progress_reporter, new_note)

        return TimePlanCreateResult(new_time_plan=new_time_plan, new_note=new_note)
