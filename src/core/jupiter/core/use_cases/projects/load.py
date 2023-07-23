"""Use case for loading a particular project."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ProjectLoadArgs(UseCaseArgsBase):
    """ProjectLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class ProjectLoadResult(UseCaseResultBase):
    """ProjectLoadResult."""

    project: Project


class ProjectLoadUseCase(
    AppLoggedInReadonlyUseCase[ProjectLoadArgs, ProjectLoadResult]
):
    """Use case for loading a particular project."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PROJECTS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: ProjectLoadArgs,
    ) -> ProjectLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            await uow.project_collection_repository.load_by_parent(
                context.workspace.ref_id,
            )
            project = await uow.project_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )

        return ProjectLoadResult(project=project)
