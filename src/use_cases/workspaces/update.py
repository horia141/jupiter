"""Command for updating a workspace."""
from dataclasses import dataclass
from typing import Final

from domain.entity_name import EntityName
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from domain.timezone import Timezone
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from models.framework import Command, UpdateAction
from utils.time_provider import TimeProvider


class WorkspaceUpdateCommand(Command['WorkspaceUpdateCommand.Args', None]):
    """Command for updating a workspace."""

    @dataclass()
    class Args:
        """Args."""
        name: UpdateAction[EntityName]
        timezone: UpdateAction[Timezone]
        default_project_key: UpdateAction[ProjectKey]

    _time_provider: Final[TimeProvider]
    _workspace_engine: Final[WorkspaceEngine]
    _notion_manager: Final[WorkspaceNotionManager]
    _project_engine: Final[ProjectEngine]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: WorkspaceEngine,
            notion_manager: WorkspaceNotionManager, project_engine: ProjectEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._workspace_engine = workspace_engine
        self._notion_manager = notion_manager
        self._project_engine = project_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._workspace_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()

            if args.name.should_change:
                workspace.change_name(args.name.value, self._time_provider.get_current_time())
            if args.timezone.should_change:
                workspace.change_timezone(args.timezone.value, self._time_provider.get_current_time())
            if args.default_project_key.should_change:
                with self._project_engine.get_unit_of_work() as project_uow:
                    project = project_uow.project_repository.load_by_key(args.default_project_key.value)
                workspace.change_default_project(project.ref_id, self._time_provider.get_current_time())

            uow.workspace_repository.save(workspace)

        self._notion_manager.upsert_workspace(workspace)
