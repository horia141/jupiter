"""Repository for workspaces."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from typing import Final, ClassVar

import pendulum
from pendulum.tz.zoneinfo import Timezone

from models.basic import Timestamp, BasicValidator
from models.framework import EntityId, JSONDictType
from models.errors import RepositoryError
from utils.storage import StructuredIndividualStorage
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MissingWorkspaceRepositoryError(RepositoryError):
    """Error raised when there isn't a workspace defined."""


@dataclass()
class Workspace:
    """A workspace."""

    name: str
    timezone: Timezone
    default_project_ref_id: typing.Optional[EntityId]
    created_time: Timestamp
    last_modified_time: Timestamp


@typing.final
class WorkspaceRepository:
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: ClassVar[Path] = Path("./workspaces.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredIndividualStorage[Workspace]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredIndividualStorage(self._WORKSPACE_FILE_PATH, self)

    def create_workspace(
            self, name: str, timezone: Timezone, default_project_ref_id: typing.Optional[EntityId]) -> Workspace:
        """Create a workspace."""
        new_workspace = Workspace(
            name=name,
            timezone=timezone,
            default_project_ref_id=default_project_ref_id,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time())
        self._structured_storage.save(new_workspace)
        return new_workspace

    def load_workspace(self) -> Workspace:
        """Load the workspace."""
        workspace = self._structured_storage.load_optional()
        if workspace is None:
            raise MissingWorkspaceRepositoryError()
        return workspace

    def save_workspace(self, new_workspace: Workspace) -> Workspace:
        """Save the workspace."""
        new_workspace.last_modified_time = self._time_provider.get_current_time()
        self._structured_storage.save(new_workspace)
        return new_workspace

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "timezone": {"type": "string"},
                "default_project_ref_id": {"type": ["string", "null"]},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> Workspace:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return Workspace(
            name=typing.cast(str, storage_form["name"]),
            timezone=pendulum.timezone(typing.cast(str, storage_form["timezone"])),
            default_project_ref_id=EntityId(typing.cast(str, storage_form["default_project_ref_id"]))
            if storage_form["default_project_ref_id"] else None,
            created_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["last_modified_time"])))

    @staticmethod
    def live_to_storage(live_form: Workspace) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "timezone": live_form.timezone.name,
            "default_project_ref_id":
                str(live_form.default_project_ref_id) if live_form.default_project_ref_id else None,
            "created_time": BasicValidator.timestamp_to_str(live_form.created_time),
            "last_modified_time": BasicValidator.timestamp_to_str(live_form.last_modified_time)
        }
