"""Load previous runs of Gen."""
from dataclasses import dataclass

from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInReadonlyUseCaseContext,
    readonly_use_case,
)


@dataclass
class GenLoadRunsArgs(UseCaseArgsBase):
    """GenLoadRunsArgs."""


@dataclass
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
        async with self._storage_engine.get_unit_of_work() as uow:
            gen_log = await uow.gen_log_repository.load_by_parent(
                context.workspace.ref_id
            )
            entries = await uow.gen_log_entry_repository.find_last(gen_log.ref_id, 30)

        return GenLoadRunsResult(entries=entries)
