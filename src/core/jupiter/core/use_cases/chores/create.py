"""The command for creating a chore."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import Feature, FeatureUnavailableError
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
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
    AppLoggedInMutationUseCase[ChoreCreateArgs, ChoreCreateResult]
):
    """The command for creating a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.CHORES

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreCreateArgs,
    ) -> ChoreCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(Feature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(Feature.PROJECTS)

        async with progress_reporter.start_creating_entity(
            "chore",
            str(args.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                chore_collection = await uow.chore_collection_repository.load_by_parent(
                    workspace.ref_id,
                )

                new_chore = Chore.new_chore(
                    chore_collection_ref_id=chore_collection.ref_id,
                    archived=False,
                    project_ref_id=args.project_ref_id
                    or workspace.default_project_ref_id,
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
                await entity_reporter.mark_known_entity_id(new_chore.ref_id)
                await entity_reporter.mark_local_change()

        return ChoreCreateResult(new_chore=new_chore)
