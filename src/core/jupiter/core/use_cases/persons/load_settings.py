"""Load settings for persons use case."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class PersonLoadSettingsArgs(UseCaseArgsBase):
    """PersonLoadSettings args."""


@dataclass
class PersonLoadSettingsResult(UseCaseResultBase):
    """PersonLoadSettings results."""

    catch_up_project: Project


class PersonLoadSettingsUseCase(
    AppLoggedInReadonlyUseCase[PersonLoadSettingsArgs, PersonLoadSettingsResult],
):
    """The command for loading the settings around persons."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: PersonLoadSettingsArgs,
    ) -> PersonLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            catch_up_project = await uow.project_repository.load_by_id(
                person_collection.catch_up_project_ref_id,
            )

        return PersonLoadSettingsResult(catch_up_project=catch_up_project)
