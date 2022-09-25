"""Integration tests for chores."""
import re

from tests.integration.infra import JupiterIntegrationTestCase


class ChoreIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for chores."""

    def test_create_chore(self) -> None:
        """Creation of a chore."""
        self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        self.go_to_notion("My Work", "Chores")

        notion_row = self.get_notion_row_in_database(
            "Clean the house", ["Period", "Eisen", "Difficulty", "Project"]
        )

        assert re.search(r"Clean the house", notion_row.title)
        assert notion_row.attributes["Period"] == "Weekly"
        assert notion_row.attributes["Eisen"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Medium"
        assert notion_row.attributes["Project"] == "Work"

        chore_out = self.jupiter("chore-show")

        assert re.search(r"Clean the house", chore_out)
        assert re.search(r"Weekly", chore_out)
        assert re.search(r"Important", chore_out)
        assert re.search(r"Medium", chore_out)
        assert re.search(r"In Project Work", chore_out)

    def test_update_chore(self) -> None:
        """Updating a chore."""
        chore_id = self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
            hint="Clean the house",
        )

        self.jupiter(
            "chore-update",
            "--id",
            chore_id,
            "--name",
            "Really clean the house",
            "--eisen",
            "regular",
            "--difficulty",
            "hard",
        )

        self.go_to_notion("My Work", "Chores")

        notion_row = self.get_notion_row_in_database(
            "Really clean the house", ["Period", "Eisen", "Difficulty", "Project"]
        )

        assert re.search(r"Really clean the house", notion_row.title)
        assert notion_row.attributes["Period"] == "Weekly"
        assert notion_row.attributes["Eisen"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Project"] == "Work"

        chore_out = self.jupiter("chore-show")

        assert re.search(r"Really clean the house", chore_out)
        assert re.search(r"Weekly", chore_out)
        assert re.search(r"Regular", chore_out)
        assert re.search(r"Hard", chore_out)
        assert re.search(r"In Project Work", chore_out)

    def test_chore_suspend(self) -> None:
        """Suspending a chore."""
        chore_id = self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
            hint="Clean the house",
        )

        self.jupiter("chore-suspend", "--id", chore_id)

        chore_out = self.jupiter("chore-show")
        assert re.search("#suspended", chore_out)

        self.jupiter("gen", "--period", "weekly", "--target", "chores")

        self.go_to_notion("My Work", "Inbox Tasks")
        assert not self.check_notion_row_exists("Clean the house")

        inbox_task_out = self.jupiter("inbox-task-show")
        assert not re.search(r"Clean the house", inbox_task_out)

    def test_chore_unsuspend(self) -> None:
        """Unsuspending a chore."""
        chore_id = self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
            hint="Clean the house",
        )

        self.jupiter("chore-suspend", "--id", chore_id)

        chore_out = self.jupiter("chore-show")
        assert re.search("#suspended", chore_out)

        self.jupiter("chore-unsuspend", "--id", chore_id)

        chore_out = self.jupiter("chore-show")
        assert not re.search("#suspended", chore_out)

    def test_chore_change_project(self) -> None:
        """Changing the catch up project for chores tasks."""
        chore_id = self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
            hint="Clean the house",
        )

        self.jupiter("chore-change-project", "--id", chore_id, "--project", "personal")

        self.go_to_notion("My Work", "Chores")

        notion_row = self.get_notion_row_in_database(
            "Clean the house", ["Period", "Eisen", "Difficulty", "Project"]
        )

        assert notion_row.attributes["Project"] == "Personal"

        chore_out = self.jupiter("chore-show")

        assert re.search(r"In Project Personal", chore_out)

    def test_archive_chore(self) -> None:
        """Archiving a chore."""
        chore_id = self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
            hint="Clean the house",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "chores")

        self.jupiter("chore-archive", "--id", chore_id)

        self.go_to_notion("My Work", "Chores")

        assert not self.check_notion_row_exists("Clean the house")

        chore_out = self.jupiter("chore-show", "--show-archived")

        assert re.search(r"Clean the house", chore_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Clean the house")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert re.search(r"Clean the house", inbox_task_out)

    def test_remove_chore(self) -> None:
        """Archiving a chore."""
        chore_id = self.jupiter_create(
            "chore-create",
            "--name",
            "Clean the house",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
            hint="Clean the house",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "chores")

        self.jupiter("chore-remove", "--id", chore_id)

        self.go_to_notion("My Work", "Chores")

        assert not self.check_notion_row_exists("Clean the house")

        chore_out = self.jupiter("chore-show", "--show-archived")

        assert not re.search(r"Clean the house", chore_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Clean the house")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert not re.search(r"Clean the house", inbox_task_out)
