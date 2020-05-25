"""Repository for workspaces."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from typing import Final, Any, ClassVar, Dict

from repository.common import RepositoryError
from utils.storage import StructuredIndividualStorage

LOGGER = logging.getLogger(__name__)


class MissingWorkspaceRepositoryError(RepositoryError):
    """Error raised when there isn't a workspace defined."""


@dataclass()
class Workspace:
    """A workspace."""

    name: str


@typing.final
class WorkspaceRepository:
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: ClassVar[Path] = Path("/data/workspaces.yaml")

    _structured_storage: Final[StructuredIndividualStorage[Workspace]]

    def __init__(self) -> None:
        """Constructor."""
        self._structured_storage = StructuredIndividualStorage(self._WORKSPACE_FILE_PATH, self)

    def create_workspace(self, name: str) -> Workspace:
        """Create a workspace."""
        new_workspace = Workspace(name=name)
        self._structured_storage.save(new_workspace)
        return new_workspace

    def load_workspace(self) -> Workspace:
        """Load the workspace."""
        workspace = self._structured_storage.load_optional()
        if workspace is None:
            raise MissingWorkspaceRepositoryError()
        return workspace

    def save_workspace(self, new_workspace: Workspace) -> None:
        """Save the workspace."""
        self._structured_storage.save(new_workspace)

    @staticmethod
    def storage_schema() -> Dict[str, Any]:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: Any) -> Workspace:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return Workspace(name=storage_form["name"])

    @staticmethod
    def live_to_storage(live_form: Workspace) -> Any:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name
        }
