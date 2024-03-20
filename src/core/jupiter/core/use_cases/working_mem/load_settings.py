"""Load settings for working mems use case."""
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.working_mem.working_mem_collection import WorkingMemCollection
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class WorkingMemLoadSettingsArgs(UseCaseArgsBase):
    """WorkingMemLoadSettings args."""


@use_case_result
class WorkingMemLoadSettingsResult(UseCaseResultBase):
    """WorkingMemLoadSettings results."""

    generation_period: RecurringTaskPeriod
    cleanup_project: Project


@readonly_use_case(WorkspaceFeature.WORKING_MEM, exclude_app=[EventSource.CLI])
class WorkingMemLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        WorkingMemLoadSettingsArgs, WorkingMemLoadSettingsResult
    ],
):
    """The command for loading the settings around workingmem."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: WorkingMemLoadSettingsArgs,
    ) -> WorkingMemLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        working_mem_collection = await uow.get_for(WorkingMemCollection).load_by_parent(
            workspace.ref_id,
        )
        catch_up_project = await uow.get_for(Project).load_by_id(
            working_mem_collection.cleanup_project_ref_id,
        )

        return WorkingMemLoadSettingsResult(
            generation_period=working_mem_collection.generation_period,
            cleanup_project=catch_up_project,
        )
