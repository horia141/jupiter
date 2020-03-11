import yaml

_WORKSPACE_FILE_PATH = "/data/workspace.yaml"

def build_empty_workspace():
    return {
        "name": None,
        "space_id": None,
        "token_v2": None,
        "vacations": []
    }

def load_workspace():
    with open(_WORKSPACE_FILE_PATH, "r") as workspace_file:
        return yaml.safe_load(workspace_file)

def save_workspace(workspace):
    with open(_WORKSPACE_FILE_PATH, "w") as workspace_file:
        yaml.dump(workspace, workspace_file)
