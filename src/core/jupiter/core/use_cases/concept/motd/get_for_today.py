"""Use case for getting a random Message of the Day."""

import hashlib

from jupiter.core.domain.concept.motd.motd import MOTD, MOTDs
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class MOTDGetForTodayArgs(UseCaseArgsBase):
    """Args for getting a MOTD."""


@use_case_result
class MOTDGetForTodayResult(UseCaseResultBase):
    """Result for getting a MOTD."""

    motd: MOTD


@readonly_use_case()
class MOTDGetForTodayUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[MOTDGetForTodayArgs, MOTDGetForTodayResult]
):
    """Use case for getting a random Message of the Day."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: MOTDGetForTodayArgs,
    ) -> MOTDGetForTodayResult:
        """Execute the command's action."""
        # Combine current date and user ID to create a deterministic seed
        today = self._time_provider.get_current_date()
        seed = f"{today}-{context.user.ref_id}"

        # Create a hash of the seed to get a number between 0 and len(MOTDs)-1
        hash_value = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        index = hash_value % len(MOTDs)

        return MOTDGetForTodayResult(motd=MOTDs[index])
