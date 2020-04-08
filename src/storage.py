"""Local storage interactions."""

from pathlib import Path
import yaml

_LOCKFILE_PATH = "/data/.system.lock"
_WORKSPACE_FILE_PATH = "/data/workspace.yaml"
_PROJECT_FILE_PATTERN = "/data/project-{0}.yaml"


def build_empty_lockfile():
    """Construct an empty lockfile."""
    return {
        "root_page_id": None,
        "projects": {}
    }


def load_lock_file():
    """Load the current lockfile, if it exists."""
    with open(_LOCKFILE_PATH) as system_lock_file:
        system_lock = yaml.safe_load(system_lock_file)
        # Sometimes an YAML serialisation error makes it so the lock file is created
        # but is empty. To counter this case we force this to be {}
        if system_lock is None:
            return {}

        return system_lock


def save_lock_file(lock):
    """Save a given lockfile."""
    with open(_LOCKFILE_PATH, "w") as project_lock_file:
        yaml.dump(lock, project_lock_file)


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


def build_empty_project():
    """Construct an empty project."""
    return {
        "key": "",
        "name": "",
        "recurring_tasks": {
            "next_idx": 0,
            "entries": {}
        }
    }


def load_project(key):
    """Load a project given by key."""
    project_file_path = _PROJECT_FILE_PATTERN.format(key)
    with open(project_file_path, "r") as project_file:
        return yaml.safe_load(project_file)


def save_project(key, project):
    """Save a project given by a key."""
    project_file_path = _PROJECT_FILE_PATTERN.format(key)
    with open(project_file_path, "w") as project_file:
        yaml.dump(project, project_file)


def remove_project(key):
    """Remove a project given by a key."""
    project_file_path = Path(_PROJECT_FILE_PATTERN.format(key))
    project_file_path.unlink()
