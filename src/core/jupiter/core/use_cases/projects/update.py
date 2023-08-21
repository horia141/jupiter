"""The command for updating a project."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class ProjectUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[ProjectName]


class ProjectUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[ProjectUpdateArgs, None]
):
    """The command for updating a project."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.PROJECTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ProjectUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        project = await uow.project_repository.load_by_id(args.ref_id)
        project = project.update(
            name=args.name,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.project_repository.save(project)
        await progress_reporter.mark_updated(project)
