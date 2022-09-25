"""The command for creating a big plan."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service import (
    InboxTaskBigPlanRefOptionsUpdateService,
)
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class BigPlanCreateUseCase(AppMutationUseCase["BigPlanCreateUseCase.Args", None]):
    """The command for creating a big plan."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        project_key: Optional[ProjectKey]
        name: BigPlanName
        actionable_date: Optional[ADate]
        due_date: Optional[ADate]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        big_plan_notion_manager: BigPlanNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with progress_reporter.start_creating_entity(
            "big plan", str(args.name)
        ) as entity_reporter:
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

                big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id
                )

                big_plan = BigPlan.new_big_plan(
                    big_plan_collection_ref_id=big_plan_collection.ref_id,
                    project_ref_id=project_ref_id,
                    archived=False,
                    name=args.name,
                    status=BigPlanStatus.ACCEPTED,
                    actionable_date=args.actionable_date,
                    due_date=args.due_date,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )
                big_plan = uow.big_plan_repository.create(big_plan)
                entity_reporter.mark_known_entity_id(
                    big_plan.ref_id
                ).mark_local_change()

            direct_info = NotionBigPlan.DirectInfo(
                all_projects_map={project.ref_id: project}
            )
            notion_big_plan = NotionBigPlan.new_notion_entity(big_plan, direct_info)
            self._big_plan_notion_manager.upsert_leaf(
                big_plan_collection.ref_id,
                notion_big_plan,
            )
            entity_reporter.mark_remote_change()

            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager
            ).sync(big_plan_collection)
            entity_reporter.mark_other_progress("inbox-task-refs")
