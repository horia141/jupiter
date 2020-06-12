"""Repository for workspaces."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from typing import Final, ClassVar

import pendulum

from repository.common import RepositoryError
from utils.storage import StructuredIndividualStorage, JSONDictType
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MissingWorkspaceRepositoryError(RepositoryError):
    """Error raised when there isn't a workspace defined."""


@dataclass()
class Workspace:
    """A workspace."""

    name: str
    created_time: pendulum.DateTime
    last_modified_time: pendulum.DateTime


@typing.final
class WorkspaceRepository:
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: ClassVar[Path] = Path("/data/workspaces.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredIndividualStorage[Workspace]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredIndividualStorage(self._WORKSPACE_FILE_PATH, self)

    def create_workspace(self, name: str) -> Workspace:
        """Create a workspace."""
        new_workspace = Workspace(
            name=name,
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
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> Workspace:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return Workspace(
            name=typing.cast(str, storage_form["name"]),
            created_time=pendulum.parse(typing.cast(str, storage_form["created_time"])),
            last_modified_time=pendulum.parse(typing.cast(str, storage_form["last_modified_time"])))

    @staticmethod
    def live_to_storage(live_form: Workspace) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "created_time": live_form.created_time.to_datetime_string(),
            "last_modified_time": live_form.last_modified_time.to_datetime_string()
        }
