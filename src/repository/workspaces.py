"""Repository for workspaces."""

import logging
import os.path
from typing import Any, ClassVar, Dict, NewType

import jsonschema as js
import yaml

from repository.common import RepositoryError

LOGGER = logging.getLogger(__name__)

WorkspaceSpaceId = NewType("WorkspaceSpaceId", str)
WorkspaceToken = NewType("WorkspaceToken", str)


class Workspace:
    """A workspace."""

    _name: str
    _space_id: WorkspaceSpaceId
    _token: WorkspaceToken

    def __init__(
            self,
            name: str,
            space_id: WorkspaceSpaceId,
            token: WorkspaceToken) -> None:
        """Constructor."""
        self._name = name
        self._space_id = space_id
        self._token = token

    def set_name(self, new_name: str) -> None:
        """Change the name of the workspace."""
        self._name = new_name

    def set_token(self, new_token: WorkspaceToken) -> None:
        """Change the token of the workspace."""
        self._token = new_token

    @property
    def name(self) -> str:
        """Name of the workspace."""
        return self._name

    @property
    def space_id(self) -> WorkspaceSpaceId:
        """Space id of the workspace."""
        return self._space_id

    @property
    def token(self) -> WorkspaceToken:
        """Access token for the workspace."""
        return self._token


class WorkspaceRepository:
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: ClassVar[str] = "/data/workspace.yaml"

    _WORKSPACE_SCHEMA: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "space_id": {"type": "string"},
            "token": {"type": "string"}
        }
    }

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
