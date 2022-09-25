"""The test case for the garbage collection functionality."""
import unittest

import pendulum

from tests.integration.infra import (
    JupiterIntegrationTestCase,
    NotionSelect,
    extract_id_from_show_out,
)


class SyncIntegrationTestCase(JupiterIntegrationTestCase):
    """The test case for the garbage collection functionality."""

    def test_vacation_archived_gc(self) -> None:
        """Garbage collection of archived vacations."""
        self.go_to_notion("My Work", "Vacations")
        self.add_notion_row(
            "Summer Trip",
            {
                "Start Date": pendulum.date(2022, 6, 10),
                "End Date": pendulum.date(2022, 6, 20),
                "Archived": True,
            },
        )

        self.jupiter("sync", "--target", "vacations")
        self.jupiter("gc", "--target", "vacations")
        assert not self.check_notion_row_exists("Summer Trip")

    @unittest.skip("Skipping because project removal cannot happen")
    def test_projects_archived_gc(self) -> None:
        """Garbage collection of archived projects."""
        self.go_to_notion("My Work", "Projects")
        self.add_notion_row(
            "Personal",
            {"Key": "personal", "Archived": True},
        )
        self.jupiter("sync", "--target", "projects")
        self.jupiter("gc", "--target", "projects")
        assert not self.check_notion_row_exists("Personal")

    def test_inbox_task_done_gc(self) -> None:
        """Garbage collection of done inbox tasks."""
        self.go_to_notion("My Work", "Inbox Tasks")
        self.add_notion_row(
            "Plan summer trip",
            {
                "Status": NotionSelect("Done"),
                "Source": NotionSelect("User"),
                "Eisenhower": NotionSelect("Urgent"),
                "Difficulty": NotionSelect("Medium"),
                "Project": NotionSelect("Work"),
            },
        )
        self.jupiter("sync", "--target", "inbox-tasks")
        self.jupiter("gc", "--target", "inbox-tasks")
        assert not self.check_notion_row_exists("Plan summer trip")

    def test_inbox_task_archived_gc(self) -> None:
        """Garbage collection of archived inbox tasks."""
        self.go_to_notion("My Work", "Inbox Tasks")
        self.add_notion_row(
            "Plan summer trip",
            {
                "Status": NotionSelect("Accepted"),
                "Source": NotionSelect("User"),
                "Eisenhower": NotionSelect("Urgent"),
                "Difficulty": NotionSelect("Medium"),
                "Project": NotionSelect("Work"),
                "Archived": True,
            },
        )
        self.jupiter("sync", "--target", "inbox-tasks")
        self.jupiter("gc", "--target", "inbox-tasks")
        assert not self.check_notion_row_exists("Plan summer trip")

    def test_habit_archived_gc(self) -> None:
        """Garbage collection of archived habits."""
        self.go_to_notion("My Work", "Habits")
        self.add_notion_row(
            "Go for a morning run",
            {
                "Period": NotionSelect("Daily"),
                "Eisenhower": NotionSelect("Regular"),
                "Difficulty": NotionSelect("Hard"),
                "Archived": True,
                "Project": NotionSelect("Work"),
            },
        )
        self.jupiter("sync", "--target", "habits")
        self.jupiter("gc", "--target", "habits")
        assert not self.check_notion_row_exists("Go for a morning run")

    def test_chore_archived_gc(self) -> None:
        """Garbage collection of archived chores."""
        self.go_to_notion("My Work", "Chores")
        self.add_notion_row(
            "Water houseplants",
            {
                "Period": NotionSelect("Weekly"),
                "Eisenhower": NotionSelect("Regular"),
                "Difficulty": NotionSelect("Easy"),
                "Archived": True,
                "Project": NotionSelect("Work"),
            },
        )
        self.jupiter("sync", "--target", "chores")
        self.jupiter("gc", "--target", "chores")
        assert not self.check_notion_row_exists("Water houseplants")

    def test_big_plan_done_gc(self) -> None:
        """Garbage collection of done big plans."""
        self.go_to_notion("My Work", "Big Plans")
        self.add_notion_row(
            "Buy a new car",
            {
                "Status": NotionSelect("Done"),
                "Actionable Date": pendulum.date(2022, 10, 1),
                "Due Date": pendulum.date(2022, 10, 27),
                "Project": NotionSelect("Work"),
            },
        )
        self.jupiter("sync", "--target", "big-plans")
        self.jupiter("gc", "--target", "big-plans")
        assert not self.check_notion_row_exists("Buy a new car")

    def test_big_plan_archived_gc(self) -> None:
        """Garbage collection of archived big plans."""
        self.go_to_notion("My Work", "Big Plans")
        self.add_notion_row(
            "Buy a new car",
            {
                "Status": NotionSelect("Accepted"),
                "Actionable Date": pendulum.date(2022, 10, 1),
                "Due Date": pendulum.date(2022, 10, 27),
                "Archived": True,
                "Project": NotionSelect("Work"),
            },
            strict_check=False,
        )
        self.jupiter("sync", "--target", "big-plans")
        self.jupiter("gc", "--target", "big-plans")
        assert not self.check_notion_row_exists("Buy a new car")

    def test_smart_list_archived_gc(self) -> None:
        """Garbage collection of archived smart lists."""
        self.jupiter_create(
            "smart-list-create",
            "--smart-list",
            "movies",
            "--name",
            "Movies",
            "--icon",
            "🎬",
        )
        self.go_to_notion("My Work", "Smart Lists", "Movies")

        self.add_notion_row(
            "Star Wars",
            {"Tags": [NotionSelect("SF"), NotionSelect("Adventure")], "Archived": True},
        )

        self.jupiter("sync", "--target", "smart-lists")
        self.jupiter("gc", "--target", "smart-lists")

        assert not self.check_notion_row_exists("Star Wars")

    def test_metric_archived_gc(self) -> None:
        """Garbage collection of archived metrics."""
        self.jupiter_create(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--collection-period",
            "weekly",
            "--unit",
            "weight",
        )
        self.go_to_notion("My Work", "Metrics", "Weight")

        self.add_notion_row(
            "First measurement",
            {
                "Collection Time": pendulum.date(2022, 10, 1),
                "Value": 80.2,
                "Archived": True,
            },
        )
        self.jupiter("sync", "--target", "metrics")
        self.jupiter("gc", "--target", "metrics")

        assert not self.check_notion_row_exists("First measurement")

    def test_person_archived_gc(self) -> None:
        """Garbage collection of archived persons."""
        self.go_to_notion("My Work", "Persons")
        self.add_notion_row(
            "Mike",
            {
                "Relationship": NotionSelect("Friend"),
                "Birthday": "17 Apr",
                "Catch Up Period": NotionSelect("Monthly"),
                "Archived": True,
            },
        )
        self.jupiter("sync", "--target", "persons")
        self.jupiter("gc", "--target", "persons")

        assert not self.check_notion_row_exists("Mike")

    def test_push_integration_slack_done_inbox_task_gc(self) -> None:
        """Garbage collection of a Slack based task with a done corresponding inbox task."""
        self.go_to_notion("My Work", "Push Integrations", "Slack")
        self.add_notion_row(
            "John Doe",
            {
                "Channel": "all-company",
                "Message": "Everybody let's prepare for our summer meetup",
                "Extra Info": "--name='Prepare for the summer meetup' --difficulty=hard",
            },
        )

        self.jupiter("sync", "--target", "slack-tasks")
        self.jupiter("gen", "--target", "slack-tasks")

        inbox_task_out = self.jupiter("inbox-task-show")
        task_id = extract_id_from_show_out(
            inbox_task_out, "Prepare for the summer meetup"
        )

        self.jupiter("inbox-task-update", "--id", task_id, "--status", "done")
        self.jupiter("gc", "--target", "slack-tasks")

        assert not self.check_notion_row_exists("John Doe")

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Prepare for the summer meetup")

    def test_push_integration_slack_archived_gc(self) -> None:
        """Garbage collection of an archived Slack based task."""
        self.go_to_notion("My Work", "Push Integrations", "Slack")
        self.add_notion_row(
            "John Doe",
            {
                "Channel": "all-company",
                "Message": "Everybody let's prepare for our summer meetup",
                "Extra Info": "--name='Prepare for the summer meetup' --difficulty=hard",
                "Archived": True,
            },
        )

        self.jupiter("sync", "--target", "slack-tasks")
        self.jupiter("gc", "--target", "slack-tasks")

        assert not self.check_notion_row_exists("John Doe")
