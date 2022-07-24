"""Integration tests for habits."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class HabitIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for habits."""

    def test_create_habit(self) -> None:
        """Creation of a habit."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        self.go_to_notion("My Work", "Habits")

        notion_row = self.get_notion_row_in_database(
            "Hit the gym", ["Period", "Eisen", "Difficulty", "Project"]
        )

        assert re.search(r"Hit the gym", notion_row.title)
        assert notion_row.attributes["Period"] == "Weekly"
        assert notion_row.attributes["Eisen"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Medium"
        assert notion_row.attributes["Project"] == "Work"

        habit_out = self.jupiter("habit-show")

        assert re.search(r"Hit the gym", habit_out)
        assert re.search(r"period=Weekly", habit_out)
        assert re.search(r"eisen=Important", habit_out)
        assert re.search(r"difficulty=Medium", habit_out)
        assert re.search(r"project=Work", habit_out)

    def test_update_habit(self) -> None:
        """Updating a habit."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        habit_out = self.jupiter("habit-show")
        habit_id = extract_id_from_show_out(habit_out, "Hit the gym")

        self.jupiter(
            "habit-update",
            "--id",
            habit_id,
            "--name",
            "Really hit the gym",
            "--eisen",
            "regular",
            "--difficulty",
            "hard",
        )

        self.go_to_notion("My Work", "Habits")

        notion_row = self.get_notion_row_in_database(
            "Really hit the gym", ["Period", "Eisen", "Difficulty", "Project"]
        )

        assert re.search(r"Really hit the gym", notion_row.title)
        assert notion_row.attributes["Period"] == "Weekly"
        assert notion_row.attributes["Eisen"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Project"] == "Work"

        habit_out = self.jupiter("habit-show")

        assert re.search(r"Really hit the gym", habit_out)
        assert re.search(r"period=Weekly", habit_out)
        assert re.search(r"eisen=Regular", habit_out)
        assert re.search(r"difficulty=Hard", habit_out)
        assert re.search(r"project=Work", habit_out)

    def test_habit_suspend(self) -> None:
        """Suspending a habit."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        habit_out = self.jupiter("habit-show")
        habit_id = extract_id_from_show_out(habit_out, "Hit the gym")

        self.jupiter("habit-suspend", "--id", habit_id)

        habit_out = self.jupiter("habit-show")
        assert re.search("suspended=True", habit_out)

        self.jupiter("gen", "--period", "weekly", "--target", "habits")

        self.go_to_notion("My Work", "Inbox Tasks", board_view="Kanban By Eisen")
        assert not self.check_notion_row_exists("Hit the gym")

        inbox_task_out = self.jupiter("inbox-task-show")
        assert not re.search(r"Hit the gym", inbox_task_out)

    def test_habit_unsuspend(self) -> None:
        """Unsuspending a habit."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        habit_out = self.jupiter("habit-show")
        habit_id = extract_id_from_show_out(habit_out, "Hit the gym")

        self.jupiter("habit-suspend", "--id", habit_id)

        habit_out = self.jupiter("habit-show")
        assert re.search("suspended=True", habit_out)

        self.jupiter("habit-unsuspend", "--id", habit_id)

        habit_out = self.jupiter("habit-show")
        assert re.search("suspended=False", habit_out)

    def test_habit_change_project(self) -> None:
        """Changing the catch up project for habits tasks."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        habit_out = self.jupiter("habit-show")
        habit_id = extract_id_from_show_out(habit_out, "Hit the gym")

        self.jupiter("habit-change-project", "--id", habit_id, "--project", "personal")

        self.go_to_notion("My Work", "Habits")

        notion_row = self.get_notion_row_in_database(
            "Hit the gym", ["Period", "Eisen", "Difficulty", "Project"]
        )

        assert notion_row.attributes["Project"] == "Personal"

        habit_out = self.jupiter("habit-show")

        assert re.search(r"project=Personal", habit_out)

    def test_archive_habit(self) -> None:
        """Archiving a habit."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "habits")

        habit_out = self.jupiter("habit-show")
        habit_id = extract_id_from_show_out(habit_out, "Hit the gym")

        self.jupiter("habit-archive", "--id", habit_id)

        self.go_to_notion("My Work", "Habits")

        assert not self.check_notion_row_exists("Hit the gym")

        habit_out = self.jupiter("habit-show", "--show-archived")

        assert re.search(r"Hit the gym", habit_out)
        assert re.search(r"archived=True", habit_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Hit the gym")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert re.search(r"Hit the gym", inbox_task_out)
        assert re.search(r"archived=True", inbox_task_out)

    def test_remove_habit(self) -> None:
        """Archiving a habit."""
        self.jupiter(
            "habit-create",
            "--name",
            "Hit the gym",
            "--period",
            "weekly",
            "--eisen",
            "important",
            "--difficulty",
            "medium",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "chores")

        habit_out = self.jupiter("habit-show")
        habit_id = extract_id_from_show_out(habit_out, "Hit the gym")

        self.jupiter("habit-remove", "--id", habit_id)

        self.go_to_notion("My Work", "Habits")

        assert not self.check_notion_row_exists("Hit the gym")

        habit_out = self.jupiter("habit-show", "--show-archived")

        assert not re.search(r"Hit the gym", habit_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Hit the gym")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert not re.search(r"Hit the gym", inbox_task_out)
