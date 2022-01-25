"""The command for updating a project."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectUpdateUseCase(AppMutationUseCase['ProjectUpdateUseCase.Args', None]):
    """The command for updating a project."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: ProjectKey
        name: UpdateAction[ProjectName]

    _project_notion_manager: Final[ProjectNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            project_notion_manager: ProjectNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._project_notion_manager = project_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            project = uow.project_repository.load_by_key(args.key)
            project = project.update(
                name=args.name, source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            uow.project_repository.save(project)
        LOGGER.info("Applied local changes")
        notion_project = self._project_notion_manager.load_project(project.ref_id)
        notion_project = notion_project.join_with_aggregate_root(project)
        self._project_notion_manager.save_project(notion_project)
        LOGGER.info("Applied Notion changes")
