"""The use case for updating the home config."""

from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    use_case_args,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class HomeConfigUpdateArgs(UseCaseArgsBase):
    """The arguments for updating the home config."""

    key_habits: UpdateAction[list[EntityId] | None]
    key_metrics: UpdateAction[list[EntityId] | None]


class HomeConfigUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeConfigUpdateArgs, None]
):
    """The use case for updating the home config."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeConfigUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        home_config = await uow.get_for(HomeConfig).load_by_parent(workspace.ref_id)

        if args.key_habits.should_change:
            if workspace.is_feature_available(WorkspaceFeature.HABITS):
                if args.key_habits.just_the_value is None:
                    raise InputValidationError("Key habits cannot be None")
                for habit_ref_id in args.key_habits.just_the_value:
                    await uow.get_for(Habit).load_by_id(
                        habit_ref_id, allow_archived=False
                    )
            else:
                if args.key_habits.just_the_value:
                    raise InputValidationError("Key habits are not enabled")

        if args.key_metrics.should_change:
            if workspace.is_feature_available(WorkspaceFeature.METRICS):
                if args.key_metrics.just_the_value is None:
                    raise InputValidationError("Key metrics cannot be None")
                for metric_ref_id in args.key_metrics.just_the_value:
                    await uow.get_for(Metric).load_by_id(
                        metric_ref_id, allow_archived=False
                    )
            else:
                if args.key_metrics.just_the_value:
                    raise InputValidationError("Key metrics are not enabled")

        updated_home_config = home_config.update(
            ctx=context.domain_context,
            key_habits=args.key_habits.transform(lambda x: x or []),
            key_metrics=args.key_metrics.transform(lambda x: x or []),
        )
        updated_home_config = await uow.get_for(HomeConfig).save(updated_home_config)
