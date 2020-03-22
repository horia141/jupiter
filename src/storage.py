"""Local storage interactions."""

import yaml

_WORKSPACE_FILE_PATH = "/data/workspace.yaml"


def build_empty_workspace():
    """Construct an empty workspace."""
    return {
        "space_id": None,
        "name": None,
        "token": None,
        "vacations": {
            "next_idx": 0,
            "entries": []
        }
    }


def load_workspace():
    """Load the current workspace."""
    with open(_WORKSPACE_FILE_PATH, "r") as workspace_file:
        return yaml.safe_load(workspace_file)


def save_workspace(workspace):
    """Save a given workspace."""
    with open(_WORKSPACE_FILE_PATH, "w") as workspace_file:
        yaml.dump(workspace, workspace_file)
