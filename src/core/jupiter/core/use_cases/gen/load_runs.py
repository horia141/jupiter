"""Load previous runs of Gen."""

from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.domain.gen.infra.gen_log_entry_repository import GenLogEntryRepository
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInReadonlyUseCaseContext,
    readonly_use_case,
)


@use_case_args
class GenLoadRunsArgs(UseCaseArgsBase):
    """GenLoadRunsArgs."""


@use_case_result
class GenLoadRunsResult(UseCaseResultBase):
    """GenLoadRunsResult."""

    entries: list[GenLogEntry]


@readonly_use_case()
class GenLoadRunsUseCase(
    AppLoggedInReadonlyUseCase[GenLoadRunsArgs, GenLoadRunsResult]
):
    """Load previous runs of task generation."""

    async def _execute(
        self,
        context: AppLoggedInReadonlyUseCaseContext,
        args: GenLoadRunsArgs,
    ) -> GenLoadRunsResult:
        """Execute the use case."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gen_log = await uow.repository_for(GenLog).load_by_parent(
                context.workspace.ref_id
            )
            entries = await uow.get_x(GenLogEntryRepository).find_last(gen_log.ref_id, 30)

        return GenLoadRunsResult(entries=entries)
