"""The command for updating a project."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ProjectUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[ProjectName]


class ProjectUpdateUseCase(AppLoggedInMutationUseCase[ProjectUpdateArgs, None]):
    """The command for updating a project."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ProjectUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity(
            "project", args.ref_id
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                project = await uow.project_repository.load_by_id(args.ref_id)
                project = project.update(
                    name=args.name,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await entity_reporter.mark_known_name(str(project.name))

                await uow.project_repository.save(project)
                await entity_reporter.mark_local_change()
