"""The command for creating a chore."""
import logging
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.chore_name import ChoreName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ChoreCreateUseCase(AppMutationUseCase["ChoreCreateUseCase.Args", None]):
    """The command for creating a chore."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        project_key: Optional[ProjectKey]
        name: ChoreName
        period: RecurringTaskPeriod
        eisen: Optional[Eisen]
        difficulty: Optional[Difficulty]
        actionable_from_day: Optional[RecurringTaskDueAtDay]
        actionable_from_month: Optional[RecurringTaskDueAtMonth]
        due_at_time: Optional[RecurringTaskDueAtTime]
        due_at_day: Optional[RecurringTaskDueAtDay]
        due_at_month: Optional[RecurringTaskDueAtMonth]
        must_do: bool
        skip_rule: Optional[RecurringTaskSkipRule]
        start_at_date: Optional[ADate]
        end_at_date: Optional[ADate]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        chore_notion_manager: ChoreNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._chore_notion_manager = chore_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )

            if args.project_key is not None:
                project = uow.project_repository.load_by_key(
                    project_collection.ref_id, args.project_key
                )
                project_ref_id = project.ref_id
            else:
                project = uow.project_repository.load_by_id(
                    workspace.default_project_ref_id
                )
                project_ref_id = workspace.default_project_ref_id

            chore_collection = uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )

            chore = Chore.new_chore(
                chore_collection_ref_id=chore_collection.ref_id,
                archived=False,
                project_ref_id=project_ref_id,
                name=args.name,
                gen_params=RecurringTaskGenParams(
                    period=args.period,
                    eisen=args.eisen if args.eisen else Eisen.REGULAR,
                    difficulty=args.difficulty,
                    actionable_from_day=args.actionable_from_day,
                    actionable_from_month=args.actionable_from_month,
                    due_at_time=args.due_at_time,
                    due_at_day=args.due_at_day,
                    due_at_month=args.due_at_month,
                ),
                skip_rule=args.skip_rule,
                start_at_date=args.start_at_date,
                end_at_date=args.end_at_date,
                suspended=False,
                must_do=args.must_do,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time(),
            )
            chore = uow.chore_repository.create(chore)
            LOGGER.info("Applied local changes")

        direct_info = NotionChore.DirectInfo(all_projects_map={project.ref_id: project})
        notion_chore = NotionChore.new_notion_entity(chore, direct_info)
        self._chore_notion_manager.upsert_leaf(
            chore_collection.ref_id,
            notion_chore,
        )
        LOGGER.info("Applied Notion changes")
