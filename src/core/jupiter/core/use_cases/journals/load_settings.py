"""Use case for loading the settings around journals."""
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase, use_case_args, use_case_result
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext, AppTransactionalLoggedInReadOnlyUseCase, readonly_use_case


@use_case_args
class JournalLoadSettingsArgs(UseCaseArgsBase):
    """JournalLoadSettings args."""

@use_case_result
class JournalLoadSettingsResult(UseCaseResultBase):
    """JournalLoadSettings results."""

    periods: list[RecurringTaskPeriod]
    writing_task_project: Project
    writing_task_gen_params: RecurringTaskGenParams


@readonly_use_case(WorkspaceFeature.JOURNALS)
class JournalLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        JournalLoadSettingsArgs, JournalLoadSettingsResult
    ],
):
    """The command for loading the settings around journals."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: JournalLoadSettingsArgs,
    ) -> JournalLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        journal_collection = await uow.journal_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        writing_task_project = await uow.project_repository.load_by_id(
            journal_collection.writing_task_project_ref_id,
        )

        return JournalLoadSettingsResult(
            periods=list(journal_collection.periods),
            writing_task_project=writing_task_project,
            writing_task_gen_params=journal_collection.writing_task_gen_params,
        )
