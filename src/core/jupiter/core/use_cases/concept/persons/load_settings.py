"""Load settings for persons use case."""

from jupiter.core.domain.app import AppCore
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.features import WorkspaceFeature
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
class PersonLoadSettingsArgs(UseCaseArgsBase):
    """PersonLoadSettings args."""


@use_case_result
class PersonLoadSettingsResult(UseCaseResultBase):
    """PersonLoadSettings results."""

    catch_up_project: Project


@readonly_use_case(WorkspaceFeature.PERSONS, exclude_app=[AppCore.CLI])
class PersonLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        PersonLoadSettingsArgs, PersonLoadSettingsResult
    ],
):
    """The command for loading the settings around persons."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: PersonLoadSettingsArgs,
    ) -> PersonLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        catch_up_project = await uow.get_for(Project).load_by_id(
            person_collection.catch_up_project_ref_id,
        )

        return PersonLoadSettingsResult(catch_up_project=catch_up_project)
