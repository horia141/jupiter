"""Load settings for email tasks use case."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
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
class SlackTaskLoadSettingsArgs(UseCaseArgsBase):
    """SlackTaskLoadSettings args."""


@dataclass
class SlackTaskLoadSettingsResult(UseCaseResultBase):
    """SlackTaskLoadSettings results."""

    generation_project: Project


class SlackTaskLoadSettingsUseCase(
    AppLoggedInReadonlyUseCase[SlackTaskLoadSettingsArgs, SlackTaskLoadSettingsResult],
):
    """The command for loading the settings around slack tasks."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SLACK_TASKS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskLoadSettingsArgs,
    ) -> SlackTaskLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
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
            generation_project = await uow.project_repository.load_by_id(
                slack_task_collection.generation_project_ref_id,
            )

        return SlackTaskLoadSettingsResult(generation_project=generation_project)
