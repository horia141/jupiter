"""The test case for the sync functionality."""
import re
import unittest

import pendulum

from tests.integration.infra import JupiterIntegrationTestCase, NotionSelect


class SyncIntegrationTestCase(JupiterIntegrationTestCase):
    """The test case for the sync functionality."""

    def test_vacation_sync(self) -> None:
        """Synchronisation of vacations."""
        self.go_to_notion("My Work", "Vacations")
        self.add_notion_row(
            "Summer Trip",
            {
                "Start Date": pendulum.date(2022, 6, 10),
                "End Date": pendulum.date(2022, 6, 20),
            },
        )
        self.jupiter("sync", "--target", "vacations")
        vacations_out = self.jupiter("vacation-show")
        assert re.search(
            r"Summer Trip start=2022-06-10 .*end=2022-06-20", vacations_out
        )

    @unittest.skip("Skipping because project removal cannot happen")
    def test_projects_sync(self) -> None:
        """Synchronisation of projects."""
        self.go_to_notion("My Work", "Projects")
        self.add_notion_row(
            "Personal",
            {"Key": "personal"},
        )
        self.jupiter("sync", "--target", "projects")
        projects_out = self.jupiter("project-show")
        assert re.search(r"Personal", projects_out)

    def test_inbox_task_sync(self) -> None:
        """Synchronisation of inbox tasks."""
        self.go_to_notion("My Work", "Inbox Tasks")
        self.add_notion_row(
            "Plan summer trip",
            {
                "Status": NotionSelect("Accepted"),
                "Source": NotionSelect("User"),
                "Eisenhower": NotionSelect("Urgent"),
                "Difficulty": NotionSelect("Medium"),
            },
        )
        self.jupiter("sync", "--target", "inbox-tasks")
        inbox_tasks_out = self.jupiter("inbox-task-show")
        assert re.search(
            r"Plan summer trip.*source=User.*status=Accepted.*eisen=Urgent.*difficulty=Medium",
            inbox_tasks_out,
        )

    def test_habit_sync(self) -> None:
        """Synchronisation of habits."""
        self.go_to_notion("My Work", "Habits")
        self.add_notion_row(
            "Go for a morning run",
            {
                "Period": NotionSelect("Daily"),
                "Eisenhower": NotionSelect("Regular"),
                "Difficulty": NotionSelect("Hard"),
            },
        )
        self.jupiter("sync", "--target", "habits")
        habit_out = self.jupiter("habit-show")
        assert re.search(
            r"Go for a morning run.*period=Daily.*eisen=Regular.*difficulty=Hard",
            habit_out,
        )

    def test_chore_sync(self) -> None:
        """Synchronisation of chores."""
        self.go_to_notion("My Work", "Chores")
        self.add_notion_row(
            "Water houseplants",
            {
                "Period": NotionSelect("Weekly"),
                "Eisenhower": NotionSelect("Regular"),
                "Difficulty": NotionSelect("Easy"),
            },
        )
        self.jupiter("sync", "--target", "chores")
        chore_out = self.jupiter("chore-show")
        assert re.search(
            r"Water houseplants.*period=Weekly.*eisen=Regular.*difficulty=Easy",
            chore_out,
        )

    def test_big_plan_sync(self) -> None:
        """Synchronisation of big plans."""
        self.go_to_notion("My Work", "Big Plans")
        self.add_notion_row(
            "Buy a new car",
            {
                "Status": NotionSelect("Accepted"),
                "Actionable Date": pendulum.date(2022, 10, 1),
                "Due Date": pendulum.date(2022, 10, 27),
            },
        )
        self.jupiter("sync", "--target", "big-plans")
        big_plan_out = self.jupiter("big-plan-show")
        assert re.search(
            r"Buy a new car.*status=Accepted.*actionable-date=2022-10-01.*due-date=2022-10-27",
            big_plan_out,
        )

    def test_smart_list_sync(self) -> None:
        """Synchronisation of smart lists."""
        self.jupiter(
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
            {"Tags": [NotionSelect("SF"), NotionSelect("Adventure")]},
        )
        self.jupiter("sync", "--target", "smart-lists")
        metric_out = self.jupiter("smart-list-show")

        assert re.search(r"movies.*🎬Movies", metric_out)
        assert re.search(r"Star Wars.*#SF.*#Adventure", metric_out)

    def test_metric_sync(self) -> None:
        """Synchronisation of metrics."""
        self.jupiter(
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
            "",
            {"Collection Time": pendulum.date(2022, 10, 1), "Value": 80.2},
        )
        self.jupiter("sync", "--target", "metrics")
        metric_out = self.jupiter("metric-show")

        assert re.search(r"weight.*Weight.*@Weekly", metric_out)
        assert re.search(r"2022-10-01", metric_out)
        assert re.search(r"val=80.2", metric_out)

    def test_person_sync(self) -> None:
        """Synchronisation of persons."""
        self.go_to_notion("My Work", "Persons")
        self.add_notion_row(
            "Mike",
            {
                "Relationship": NotionSelect("Friend"),
                "Birthday": "17 Apr",
                "Catch Up Period": NotionSelect("Monthly"),
            },
        )
        self.jupiter("sync", "--target", "persons")
        person_out = self.jupiter("person-show")
        assert re.search(r"Mike.*Friend.*Catch up Monthly.*17 Apr", person_out)

    def test_push_integration_slack_sync(self) -> None:
        """Synchronisation of a Slack based task via a push integration."""
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
        slack_task_out = self.jupiter("slack-task-show")
        assert re.search(r"name=Prepare for the summer meetup", slack_task_out)
        assert re.search(r"from=John Doe", slack_task_out)
        assert re.search(r"in-channel=all-company", slack_task_out)
        assert re.search(r"difficulty=Hard", slack_task_out)
        assert re.search(r"channel=all-company", slack_task_out)
