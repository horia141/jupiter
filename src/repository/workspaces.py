"""Repository for workspaces."""

from dataclasses import dataclass
import logging
import os.path
import typing
from typing import Final, Any, ClassVar, Dict, NewType

import jsonschema as js
import yaml

from repository.common import RepositoryError

LOGGER = logging.getLogger(__name__)

WorkspaceSpaceId = NewType("WorkspaceSpaceId", str)
WorkspaceToken = NewType("WorkspaceToken", str)


@dataclass()
class Workspace:
    """A workspace."""

    name: str
    space_id: WorkspaceSpaceId
    token: WorkspaceToken


@typing.final
class WorkspaceRepository:
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: Final[ClassVar[str]] = "/data/workspace.yaml"

    _WORKSPACE_SCHEMA: Final[ClassVar[Dict[str, Any]]] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "space_id": {"type": "string"},
            "token": {"type": "string"}
        }
    }

    _validator: Final[Any]

    def __init__(self) -> None:
        """Constructor."""
        custom_type_checker = js.Draft6Validator.TYPE_CHECKER

        self._validator = js.validators.extend(js.Draft6Validator, type_checker=custom_type_checker)

    def initialize(self) -> None:
        """Initialise the repository."""
        if os.path.exists(WorkspaceRepository._WORKSPACE_FILE_PATH):
            return
        dummy_workspace = Workspace("dummy", WorkspaceSpaceId("FAKE_IT"), WorkspaceToken("TILL_YOU_MAKE_IT"))
        self.save_workspace(dummy_workspace)

    def load_workspace(self) -> Workspace:
        """Load the workspace."""
        try:
            with open(self._WORKSPACE_FILE_PATH, "r") as workspace_file:
                workspace_ser = yaml.safe_load(workspace_file)
                LOGGER.info("Loaded workspace")

                self._validator(WorkspaceRepository._WORKSPACE_SCHEMA).validate(workspace_ser)
                LOGGER.info("Checked workspace structure")

                workspace = Workspace(
                    workspace_ser["name"],
                    WorkspaceSpaceId(workspace_ser["space_id"]),
                    WorkspaceToken(workspace_ser["token"]))

                return workspace
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    def save_workspace(self, new_workspace: Workspace) -> None:
        """Save the workspace."""
        try:
            with open(self._WORKSPACE_FILE_PATH, "w") as workspace_file:
                new_workspace_ser = {
                    "name": new_workspace.name,
                    "space_id": new_workspace.space_id,
                    "token": new_workspace.token
                }

                self._validator(WorkspaceRepository._WORKSPACE_SCHEMA).validate(new_workspace_ser)
                LOGGER.info("Checked workspace structure")

                yaml.dump(new_workspace_ser, workspace_file)
                LOGGER.info("Saved workspace")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error
