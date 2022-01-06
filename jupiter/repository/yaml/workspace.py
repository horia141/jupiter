"""Repository for workspaces."""
import logging
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Final, ClassVar

from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository, WorkspaceNotFoundError, \
    WorkspaceAlreadyExistsError
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.repository.yaml.infra.storage import StructuredIndividualStorage
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _WorkspaceRow:
    """A workspace."""

    version: int
    name: WorkspaceName
    timezone: Timezone
    default_project_ref_id: EntityId
    created_time: Timestamp
    last_modified_time: Timestamp


class YamlWorkspaceRepository(WorkspaceRepository):
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: ClassVar[Path] = Path("./workspaces.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredIndividualStorage[_WorkspaceRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredIndividualStorage(self._WORKSPACE_FILE_PATH, self)

    def initialize(self) -> None:
        """Initialise the workspace repository."""

    def create(self, workspace: Workspace) -> Workspace:
        """Create a new workspace."""
        workspace_row = self._structured_storage.load_optional()
        if workspace_row is not None:
            raise WorkspaceAlreadyExistsError("A workspace already exists")
        new_workspace_row = _WorkspaceRow(
            version=workspace.version,
            name=workspace.name,
            timezone=workspace.timezone,
            default_project_ref_id=workspace.default_project_ref_id,
            created_time=workspace.created_time,
            last_modified_time=workspace.last_modified_time)
        self._structured_storage.save(new_workspace_row)
        return workspace

    def save(self, workspace: Workspace) -> Workspace:
        """Save the workspace."""
        new_workspace_row = _WorkspaceRow(
            version=workspace.version,
            name=workspace.name,
            timezone=workspace.timezone,
            default_project_ref_id=workspace.default_project_ref_id,
            created_time=workspace.created_time,
            last_modified_time=workspace.last_modified_time)
        self._structured_storage.save(new_workspace_row)
        return workspace

    def load(self) -> Workspace:
        """Find the workspace."""
        workspace_row = self._structured_storage.load_optional()
        if workspace_row is None:
            raise WorkspaceNotFoundError(f"The workspace does not exist")
        return Workspace(
            ref_id=BAD_REF_ID,
            version=workspace_row.version,
            archived=False,
            created_time=workspace_row.created_time,
            archived_time=None,
            last_modified_time=workspace_row.last_modified_time,
            events=[],
            name=workspace_row.name,
            timezone=workspace_row.timezone,
            default_project_ref_id=workspace_row.default_project_ref_id)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "version": {"type": "number"},
                "name": {"type": "string"},
                "timezone": {"type": "string"},
                "default_project_ref_id": {"type": "string"},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _WorkspaceRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _WorkspaceRow(
            version=typing.cast(int, storage_form["version"]),
            name=WorkspaceName.from_raw(typing.cast(str, storage_form["name"])),
            timezone=Timezone.from_raw(typing.cast(str, storage_form["timezone"])),
            default_project_ref_id=EntityId.from_raw(typing.cast(str, storage_form["default_project_ref_id"])),
            created_time=Timestamp.from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=Timestamp.from_str(typing.cast(str, storage_form["last_modified_time"])))

    @staticmethod
    def live_to_storage(live_form: _WorkspaceRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "version": live_form.version,
            "name": str(live_form.name),
            "timezone": str(live_form.timezone),
            "default_project_ref_id": str(live_form.default_project_ref_id),
            "created_time": str(live_form.created_time),
            "last_modified_time": str(live_form.last_modified_time)
        }
