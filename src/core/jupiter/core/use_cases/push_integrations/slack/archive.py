"""The command for archiving a slack task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.push_integrations.slack.service.archive_service import (
    SlackTaskArchiveService,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SlackTaskArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SlackTaskArchiveUseCase(AppLoggedInMutationUseCase[SlackTaskArchiveArgs, None]):
    """The command for archiving a slack task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SLACK_TASKS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            slack_task = await uow.slack_task_repository.load_by_id(ref_id=args.ref_id)

        slack_task_archive_service = SlackTaskArchiveService(
            EventSource.CLI,
            self._time_provider,
            self._domain_storage_engine,
        )

        await slack_task_archive_service.do_it(progress_reporter, slack_task)
