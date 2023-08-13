"""Use case for removing a project."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.domain.projects.service.remove_service import ProjectRemoveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ProjectRemoveArgs(UseCaseArgsBase):
    """Project remove args."""

    ref_id: EntityId
    backup_project_ref_id: Optional[EntityId] = None


class ProjectRemoveUseCase(AppLoggedInMutationUseCase[ProjectRemoveArgs, None]):
    """The command for removing a project."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PROJECTS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ProjectRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        if args.backup_project_ref_id:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                if context.workspace.default_project_ref_id == args.ref_id:
                    workspace = context.workspace.change_default_project(
                        args.backup_project_ref_id,
                        EventSource.CLI,
                        self._time_provider.get_current_time(),
                    )
                    await uow.workspace_repository.save(workspace)

                metric_collection = (
                    await uow.metric_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )
                if metric_collection.collection_project_ref_id == args.ref_id:
                    metric_collection = metric_collection.change_collection_project(
                        args.backup_project_ref_id,
                        EventSource.CLI,
                        self._time_provider.get_current_time(),
                    )
                    await uow.metric_collection_repository.save(metric_collection)

                person_collection = (
                    await uow.person_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )
                if person_collection.catch_up_project_ref_id == args.ref_id:
                    person_collection = person_collection.change_catch_up_project(
                        args.backup_project_ref_id,
                        EventSource.CLI,
                        self._time_provider.get_current_time(),
                    )
                    await uow.person_collection_repository.save(person_collection)

                push_integration_group = (
                    await uow.push_integration_group_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )
                slack_task_collection = (
                    await uow.slack_task_collection_repository.load_by_parent(
                        push_integration_group.ref_id,
                    )
                )
                if slack_task_collection.generation_project_ref_id == args.ref_id:
                    slack_task_collection = (
                        slack_task_collection.change_generation_project(
                            args.backup_project_ref_id,
                            EventSource.CLI,
                            self._time_provider.get_current_time(),
                        )
                    )
                    await uow.slack_task_collection_repository.save(
                        slack_task_collection
                    )

                push_integration_group = (
                    await uow.push_integration_group_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )
                email_task_collection = (
                    await uow.email_task_collection_repository.load_by_parent(
                        push_integration_group.ref_id,
                    )
                )
                if email_task_collection.generation_project_ref_id == args.ref_id:
                    email_task_collection = (
                        email_task_collection.change_generation_project(
                            args.backup_project_ref_id,
                            EventSource.CLI,
                            self._time_provider.get_current_time(),
                        )
                    )
                    await uow.email_task_collection_repository.save(
                        email_task_collection
                    )

        project_remove_service = ProjectRemoveService(
            EventSource.CLI, self._time_provider, self._domain_storage_engine
        )
        await project_remove_service.do_it(
            progress_reporter, context.workspace, args.ref_id
        )
