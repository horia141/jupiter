"""Test case for the init functionality."""
import re
import uuid

from tests.integration.infra import JupiterBasicIntegrationTestCase


class InitIntegrationTestCase(JupiterBasicIntegrationTestCase):
    """Test case for the init functionality."""

    def test_init(self) -> None:
        """Test the init function."""
        unique_id = str(uuid.uuid4())
        sqlite_db_path = self.cache_path / f"jupiter-{unique_id}.sqlite"
        workspace_name = f"My Work {unique_id}"

        try:
            self.jupiter(
                "init",
                "--name",
                workspace_name,
                "--timezone",
                "Europe/Bucharest",
                "--notion-space-id",
                self.space_id,
                "--notion-token",
                self.token_v2,
                "--notion-api-token",
                self.notion_api_token,
                "--project-key",
                "work",
                "--project-name",
                "Work",
                sqlite_db_path=sqlite_db_path,
            )

            self.go_to_notion(workspace_name, "Vacations")
            self.go_to_notion(workspace_name, "Projects")
            self.go_to_notion(workspace_name, "Inbox Tasks")
            self.go_to_notion(workspace_name, "Habits")
            self.go_to_notion(workspace_name, "Chores")
            self.go_to_notion(workspace_name, "Big Plans")
            self.go_to_notion(workspace_name, "Smart Lists")
            self.go_to_notion(workspace_name, "Metrics")
            self.go_to_notion(workspace_name, "Persons")
            self.go_to_notion(workspace_name, "Push Integrations", "Slack")

            workspace_out = self.jupiter(
                "workspace-show", sqlite_db_path=sqlite_db_path
            )

            assert re.search(workspace_name, workspace_out)
            assert re.search(r"Europe/Bucharest", workspace_out)
            assert re.search(r"In Project Work", workspace_out)
        finally:
            self.jupiter("test-helper-nuke", sqlite_db_path=sqlite_db_path)
