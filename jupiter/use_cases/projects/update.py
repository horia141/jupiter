"""The command for updating a project."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.entity_name import EntityName
from jupiter.domain.projects.infra.project_engine import ProjectEngine
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectUpdateUseCase(UseCase['ProjectUpdateUseCase.Args', None]):
    """The command for updating a project."""

    @dataclass()
    class Args:
        """Args."""
        key: ProjectKey
        name: UpdateAction[EntityName]

    _time_provider: Final[TimeProvider]
    _project_engine: Final[ProjectEngine]
    _project_notion_manager: Final[ProjectNotionManager]

    def __init__(
            self, time_provider: TimeProvider, project_engine: ProjectEngine,
            project_notion_manager: ProjectNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._project_engine = project_engine
        self._project_notion_manager = project_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._project_engine.get_unit_of_work() as uow:
            project = uow.project_repository.load_by_key(args.key)
            if args.name.should_change:
                project.change_name(args.name.value, self._time_provider.get_current_time())
            uow.project_repository.save(project)
        LOGGER.info("Applied local changes")
        notion_project = self._project_notion_manager.load_project(project.ref_id)
        notion_project = notion_project.join_with_aggregate_root(project)
        self._project_notion_manager.save_project(notion_project)
        LOGGER.info("Applied Notion changes")
