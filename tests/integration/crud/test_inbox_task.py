"""Integration tests for inbox tasks."""
import re

from tests.integration.infra import (
    JupiterIntegrationTestCase,
    BetterMatch,
)


class InboxTaskIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for inbox tasks."""

    def test_create_inbox_task(self) -> None:
        """Creation of a inbox task."""
        self.jupiter(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
        )

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Take kitty to the vet",
            ["Status", "Source", "Eisenhower", "Difficulty", "Due Date", "Project"],
        )

        assert re.search(r"Take kitty to the vet", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "User"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Due Date"] == "May 20, 2022"
        assert notion_row.attributes["Project"] == "Work"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Take kitty to the vet", inbox_task_out)
        assert re.search(r"🔧", inbox_task_out)
        assert re.search(r"User", inbox_task_out)
        assert re.search(r"Important", inbox_task_out)
        assert re.search(r"Hard", inbox_task_out)
        assert re.search(r"Due at 2022-05-20", inbox_task_out)
        assert re.search(r"In Project Work", inbox_task_out)

    def test_create_inbox_task_for_big_plan(self) -> None:
        """Creation of a inbox task."""
        big_plan_id = self.jupiter_create(
            "big-plan-create", "--name", "Get a cat", hint="Get a cat"
        )

        self.jupiter_create(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
            "--big-plan",
            big_plan_id,
        )

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Take kitty to the vet",
            [
                "Status",
                "Source",
                "Eisenhower",
                "Difficulty",
                "Due Date",
                "Project",
                BetterMatch("Big Plan", "Get a cat"),
            ],
        )

        assert re.search(r"Take kitty to the vet", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "Big Plan"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Due Date"] == "May 20, 2022"
        assert notion_row.attributes["Project"] == "Work"
        assert notion_row.attributes["Big Plan"] == "Get a cat"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Take kitty to the vet", inbox_task_out)
        assert re.search(r"🔧", inbox_task_out)
        assert re.search(r"Big Plan", inbox_task_out)
        assert re.search(r"Important", inbox_task_out)
        assert re.search(r"Hard", inbox_task_out)
        assert re.search(r"Due at 2022-05-20", inbox_task_out)
        assert re.search(r"In Project( )+Work", inbox_task_out)
        assert re.search(r"From @Get a cat", inbox_task_out)

    def test_update_inbox_task(self) -> None:
        """Updating a inbox task."""
        inbox_task_id = self.jupiter_create(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
            hint="Take kitty to the vet",
        )

        self.jupiter(
            "inbox-task-update",
            "--id",
            inbox_task_id,
            "--status",
            "in-progress",
            "--name",
            "Take the kitty to the vet",
            "--eisen",
            "regular",
            "--difficulty",
            "medium",
            "--due-date",
            "2022-05-21",
        )

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Take the kitty to the vet",
            ["Status", "Source", "Eisenhower", "Difficulty", "Due Date", "Project"],
        )

        assert re.search(r"Take the kitty to the vet", notion_row.title)
        assert notion_row.attributes["Status"] == "In Progress"
        assert notion_row.attributes["Source"] == "User"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Medium"
        assert notion_row.attributes["Due Date"] == "May 21, 2022"
        assert notion_row.attributes["Project"] == "Work"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Take the kitty to the vet", inbox_task_out)
        assert re.search(r"🚧", inbox_task_out)
        assert re.search(r"User", inbox_task_out)
        assert re.search(r"Regular", inbox_task_out)
        assert re.search(r"Medium", inbox_task_out)
        assert re.search(r"Due at 2022-05-21", inbox_task_out)
        assert re.search(r"In Project Work", inbox_task_out)

    def test_associate_with_big_plan(self) -> None:
        """Associating a task with a big plan."""
        big_plan_id = self.jupiter_create(
            "big-plan-create", "--name", "Get a cat", hint="Get a cat"
        )
        inbox_task_id = self.jupiter_create(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
            hint="Take kitty to the vet",
        )

        self.jupiter(
            "inbox-task-associate-with-big-plan",
            "--id",
            inbox_task_id,
            "--big-plan-id",
            big_plan_id,
        )

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Take kitty to the vet",
            [
                "Status",
                "Source",
                "Eisenhower",
                "Difficulty",
                "Due Date",
                "Project",
                BetterMatch("Big Plan", "Get a cat"),
            ],
        )

        assert re.search(r"Take kitty to the vet", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "Big Plan"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Due Date"] == "May 20, 2022"
        assert notion_row.attributes["Project"] == "Work"
        assert notion_row.attributes["Big Plan"] == "Get a cat"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Take kitty to the vet", inbox_task_out)
        assert re.search(r"🔧", inbox_task_out)
        assert re.search(r"Big Plan", inbox_task_out)
        assert re.search(r"Important", inbox_task_out)
        assert re.search(r"Hard", inbox_task_out)
        assert re.search(r"Due at 2022-05-20", inbox_task_out)
        assert re.search(r"From @Get a cat", inbox_task_out)
        assert re.search(r"In Project( )+Work", inbox_task_out)

    def test_change_project(self) -> None:
        """Change the project of an inbox task."""
        inbox_task_id = self.jupiter_create(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
            hint="Take kitty to the vet",
        )

        self.jupiter(
            "inbox-task-change-project", "--id", inbox_task_id, "--project", "personal"
        )

        notion_row = self.get_notion_row(
            "Take kitty to the vet",
            [
                "Status",
                "Source",
                "Eisenhower",
                "Difficulty",
                "Due Date",
                BetterMatch("Project", "Personal"),
            ],
        )

        assert re.search(r"Take kitty to the vet", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "User"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert re.search(r"May 20, 2022", notion_row.attributes["Due Date"])
        assert notion_row.attributes["Project"] == "Personal"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Take kitty to the vet", inbox_task_out)
        assert re.search(r"🔧", inbox_task_out)
        assert re.search(r"User", inbox_task_out)
        assert re.search(r"Important", inbox_task_out)
        assert re.search(r"Hard", inbox_task_out)
        assert re.search(r"Due at 2022-05-20", inbox_task_out)
        assert re.search(r"In Project Personal", inbox_task_out)

    def test_archive_inbox_task(self) -> None:
        """Archiving a inbox task."""
        inbox_task_id = self.jupiter_create(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
            hint="Take kitty to the vet",
        )

        self.jupiter("inbox-task-archive", "--id", inbox_task_id)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Take kitty to the vet")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert re.search(r"Take kitty to the vet", inbox_task_out)

    def test_remove_inbox_task(self) -> None:
        """Archiving a inbox task."""
        inbox_task_id = self.jupiter_create(
            "inbox-task-create",
            "--name",
            "Take kitty to the vet",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-20",
            hint="Take kitty to the vet",
        )

        self.jupiter("inbox-task-remove", "--id", inbox_task_id)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Take kitty to the vet")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert not re.search(r"Take kitty to the vet", inbox_task_out)
