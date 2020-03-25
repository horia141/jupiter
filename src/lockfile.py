"""Module for dealing with lockfiles - simple databases of Notion information."""

import yaml

_LOCKFILE_PATH = "/data/.system.lock"


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
