"A use case for regenerating tasks associated with metrics."
from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)


@use_case_args
class MetricRegenArgs(UseCaseArgsBase):
    """The arguments for the metric regen use case."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricRegenUseCase(AppLoggedInMutationUseCase[MetricRegenArgs, None]):
    """A use case for regenerating tasks associated with metrics."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricRegenArgs,
    ) -> None:
        """Perform the mutation."""
        gen_service = GenService(
            domain_storage_engine=self._domain_storage_engine,
        )

        await gen_service.do_it(
            ctx=context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=True,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.METRICS],
            period=None,
            filter_metric_ref_ids=[args.ref_id],
        )
