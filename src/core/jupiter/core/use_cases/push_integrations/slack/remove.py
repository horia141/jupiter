"""The command for hard removing a slack task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SlackTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SlackTaskRemoveUseCase(AppLoggedInMutationUseCase[SlackTaskRemoveArgs, None]):
    """The command for archiving a slack task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SLACK_TASKS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            slack_task = await uow.slack_task_repository.load_by_id(ref_id=args.ref_id)

        slack_task_remove_service = SlackTaskRemoveService(
            self._storage_engine,
        )

        await slack_task_remove_service.do_it(progress_reporter, slack_task)
