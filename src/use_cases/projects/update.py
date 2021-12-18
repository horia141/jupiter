"""The command for updating a project."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.entity_name import EntityName
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.infra.project_notion_manager import ProjectNotionManager
from domain.projects.project_key import ProjectKey
from models.framework import Command, UpdateAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectUpdateCommand(Command['ProjectUpdateCommand.Args', None]):
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
            project = uow.project_repository.get_by_key(args.key)
            if args.name.should_change:
                project.change_name(args.name.value, self._time_provider.get_current_time())
            uow.project_repository.save(project)
        LOGGER.info("Applied local changes")
        self._project_notion_manager.upsert(project)
        LOGGER.info("Applied Notion changes")
