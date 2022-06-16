"""Integration tests for projects."""
import re
import unittest

from tests.integration.infra import JupiterIntegrationTestCase


@unittest.skip("Skipping because project removal cannot happen")
class ProjectIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for projects."""

    def test_create_project(self) -> None:
        """Creation of a project."""
        self.jupiter("project-create", "--project", "startup", "--name", "Startup")

        self.go_to_notion("My Work", "Projects")

        notion_row = self.get_notion_row_in_database("Startup", ["Key"])

        assert re.search(r"Startup", notion_row.title)
        assert notion_row.attributes["Key"] == "startup"

        project_out = self.jupiter("project-show")

        assert re.search(r"Startup", project_out)
        assert re.search(r"startup", project_out)

    def test_update_project(self) -> None:
        """Updating a project."""
        self.jupiter("project-create", "--project", "startup", "--name", "Startup")

        self.jupiter("project-update", "--project", "startup", "--name", "The Startup")

        self.go_to_notion("My Work", "Projects")

        notion_row = self.get_notion_row_in_database("Startup", ["Key"])

        assert re.search(r"THe Startup", notion_row.title)
        assert notion_row.attributes["Key"] == "startup"

        project_out = self.jupiter("project-show")

        assert re.search(r"The Startup", project_out)
        assert re.search(r"startup", project_out)
