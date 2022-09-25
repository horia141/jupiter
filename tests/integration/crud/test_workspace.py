"""Integration tests for workspaces."""
import re

from tests.integration.infra import JupiterIntegrationTestCase


class WorkspaceIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for workspaces."""

    def test_update_workspace(self) -> None:
        """Update a workspace."""
        self.jupiter(
            "workspace-update", "--name", "My Big Work", "--timezone", "Europe/London"
        )

        self.go_to_notion("My Big Work")

        workspace_out = self.jupiter("workspace-show")

        assert re.search("My Big Work", workspace_out)
        assert re.search("Europe/London", workspace_out)
        assert re.search("In Project Work", workspace_out)

    def test_change_default_project(self) -> None:
        """Change the default project."""
        self.jupiter(
            "workspace-change-default-project", "--default-project", "Personal"
        )

        self.jupiter("inbox-task-create", "--name", "Take kitty to the vet")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Take kitty to the vet",
            ["Project"],
        )

        assert notion_row.attributes["Project"] == "Personal"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search("In Project Personal", inbox_task_out)

        workspace_out = self.jupiter("workspace-show")

        assert re.search("In Project Personal", workspace_out)
