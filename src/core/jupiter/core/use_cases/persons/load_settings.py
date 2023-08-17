"""Load settings for persons use case."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class PersonLoadSettingsArgs(UseCaseArgsBase):
    """PersonLoadSettings args."""


@dataclass
class PersonLoadSettingsResult(UseCaseResultBase):
    """PersonLoadSettings results."""

    catch_up_project: Project


class PersonLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        PersonLoadSettingsArgs, PersonLoadSettingsResult
    ],
):
    """The command for loading the settings around persons."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.PERSONS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: PersonLoadSettingsArgs,
    ) -> PersonLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.person_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        catch_up_project = await uow.project_repository.load_by_id(
            person_collection.catch_up_project_ref_id,
        )

        return PersonLoadSettingsResult(catch_up_project=catch_up_project)
