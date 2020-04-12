"""Repository for workspaces."""

import logging
from typing import NewType, List, Sequence

import jsonschema as js
import yaml

from service.common import RepositoryError

LOGGER = logging.getLogger(__name__)

WorkspaceSpaceId = NewType("WorkspaceSpaceId", str)
WorkspaceToken = NewType("WorkspaceToken", str)


class Workspace:
    """A workspace."""

    _name: str
    _space_id: WorkspaceSpaceId
    _token: WorkspaceToken
    _projects_meta: List[str]

    def __init__(
            self,
            name: str,
            space_id: WorkspaceSpaceId,
            token: WorkspaceToken,
            projects_meta: List[str]) -> None:
        """Constructor."""
        self._name = name
        self._space_id = space_id
        self._token = token
        self._projects_meta = projects_meta

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

    @property
    def projects_meta(self) -> Sequence[str]:
        """The keys of all the projects."""
        return self._projects_meta


class WorkspaceRepository:
    """A repository for workspaces."""

    _WORKSPACE_FILE_PATH: str = "/data/workspace.yaml"

    _WORKSPACE_SCHEMA = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "space_id": {"type": "string"},
            "token": {"type": "string"},
            "projects_meta": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }

    def __init__(self) -> None:
        """Constructor."""
        custom_type_checker = js.Draft6Validator.TYPE_CHECKER

        self._validator = js.validators.extend(js.Draft6Validator, type_checker=custom_type_checker)

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
                    WorkspaceToken(workspace_ser["token"]),
                    workspace_ser["projects_meta"])

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
                    "token": new_workspace.token,
                    "projects_meta": new_workspace.projects_meta
                }

                self._validator(WorkspaceRepository._WORKSPACE_SCHEMA).validate(new_workspace_ser)
                LOGGER.info("Checked workspace structure")

                yaml.dump(new_workspace_ser, workspace_file)
                LOGGER.info("Saved workspace")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error
