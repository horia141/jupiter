"""The command for creating a chore."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    UserFeature,
    WorkspaceFeature,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class ChoreCreateArgs(UseCaseArgsBase):
    """ChoreCreate args."""

    name: ChoreName
    period: RecurringTaskPeriod
    project_ref_id: Optional[EntityId] = None
    eisen: Optional[Eisen] = None
    difficulty: Optional[Difficulty] = None
    actionable_from_day: Optional[RecurringTaskDueAtDay] = None
    actionable_from_month: Optional[RecurringTaskDueAtMonth] = None
    due_at_time: Optional[RecurringTaskDueAtTime] = None
    due_at_day: Optional[RecurringTaskDueAtDay] = None
    due_at_month: Optional[RecurringTaskDueAtMonth] = None
    must_do: bool = False
    skip_rule: Optional[RecurringTaskSkipRule] = None
    start_at_date: Optional[ADate] = None
    end_at_date: Optional[ADate] = None


@dataclass
class ChoreCreateResult(UseCaseResultBase):
    """ChoreCreate result."""

    new_chore: Chore


class ChoreCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreCreateArgs, ChoreCreateResult]
):
    """The command for creating a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.CHORES

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreCreateArgs,
    ) -> ChoreCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        chore_collection = await uow.chore_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        new_chore = Chore.new_chore(
            chore_collection_ref_id=chore_collection.ref_id,
            archived=False,
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
            name=args.name,
            gen_params=RecurringTaskGenParams(
                period=args.period,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_from_day=args.actionable_from_day,
                actionable_from_month=args.actionable_from_month,
                due_at_time=args.due_at_time,
                due_at_day=args.due_at_day,
                due_at_month=args.due_at_month,
            ),
            start_at_date=args.start_at_date,
            end_at_date=args.end_at_date,
            skip_rule=args.skip_rule,
            suspended=False,
            must_do=args.must_do,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        new_chore = await uow.chore_repository.create(new_chore)
        await progress_reporter.mark_created(new_chore)

        return ChoreCreateResult(new_chore=new_chore)
