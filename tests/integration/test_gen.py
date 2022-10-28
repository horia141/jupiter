"""The test case for the gen functionality."""
import re

from tests.integration.infra import JupiterIntegrationTestCase


class GenIntegrationTestCase(JupiterIntegrationTestCase):
    """Test case for the gen functionality."""

    def test_habit_generation(self) -> None:
        """Generation of habits."""
        self.jupiter_create(
            "habit-create", "--name", "Hit the gym", "--period", "weekly"
        )
        self.jupiter("gen", "--period", "weekly")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Hit the gym", ["Status", "Source", "Eisenhower", "Difficulty", "Project"]
        )

        assert re.search(r"Hit the gym \d\d:W(\d|\d\d)", notion_row.title)
        assert notion_row.attributes["Status"] == "Recurring"
        assert notion_row.attributes["Source"] == "Habit"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Empty"
        assert notion_row.attributes["Project"] == "Work"

    def test_chore_generation(self) -> None:
        """Generation of habits."""
        self.jupiter_create(
            "chore-create", "--name", "Clean the house", "--period", "weekly"
        )
        self.jupiter("gen", "--period", "weekly")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Clean the house",
            ["Status", "Source", "Eisenhower", "Difficulty", "Project"],
        )

        assert re.search(r"Clean the house \d\d:W(\d|\d\d)", notion_row.title)
        assert notion_row.attributes["Status"] == "Recurring"
        assert notion_row.attributes["Source"] == "Chore"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Empty"
        assert notion_row.attributes["Project"] == "Work"

    def test_metric_generation(self) -> None:
        """Generation of metrics."""
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
        self.jupiter("gen", "--period", "weekly")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Collect value for metric Weight",
            ["Status", "Source", "Eisenhower", "Difficulty", "Project"],
        )

        assert re.search(
            r"Collect value for metric Weight \d\d:W(\d|\d\d)", notion_row.title
        )
        assert notion_row.attributes["Status"] == "Recurring"
        assert notion_row.attributes["Source"] == "Metric"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Empty"
        assert notion_row.attributes["Project"] == "Work"

    def test_person_catch_up_generation(self) -> None:
        """Generation of person catch up tasks."""
        self.jupiter_create(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--catch-up-period",
            "weekly",
        )
        self.jupiter("gen", "--period", "weekly")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Catch up with Mike",
            ["Status", "Source", "Eisenhower", "Difficulty", "Project"],
        )

        assert re.search(r"Catch up with Mike \d\d:W(\d|\d\d)", notion_row.title)
        assert notion_row.attributes["Status"] == "Recurring"
        assert notion_row.attributes["Source"] == "Person Catch Up"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Empty"
        assert notion_row.attributes["Project"] == "Work"

    def test_person_birthday_generation(self) -> None:
        """Generation of person catch up tasks."""
        self.jupiter_create(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--birthday",
            "7 Jan",
        )
        self.jupiter("gen")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Wish happy birthday to Mike",
            ["Status", "Source", "Eisenhower", "Difficulty", "Project"],
        )

        assert re.search(r"Wish happy birthday to Mike \d\d", notion_row.title)
        assert notion_row.attributes["Status"] == "Recurring"
        assert notion_row.attributes["Source"] == "Person Birthday"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Easy"
        assert notion_row.attributes["Project"] == "Work"

    def test_push_integration_slack(self) -> None:
        """Generation of a Slack based task via a push integration."""
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
        self.jupiter("gen")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Prepare for the summer meetup",
            ["Status", "Source", "Eisenhower", "Difficulty", "Project"],
        )

        assert re.search(r"Prepare for the summer meetup", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "Slack Task"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Project"] == "Work"
        assert re.search(r"[*][*]user[*][*]: John Doe", notion_row.page_content)
        assert re.search(r"[*][*]channel[*][*]: all-company", notion_row.page_content)
        assert re.search(
            r"[*][*]message[*][*]: Everybody let’s prepare for our summer meetup",
            notion_row.page_content,
        )

    def test_push_integration_email(self) -> None:
        """Generation of a slack based task via a push integration."""
        self.go_to_notion("My Work", "Push Integrations", "Email")
        self.add_notion_row(
            "Time for the summer meetup",
            {
                "To Address": "horia@example.com",
                "Body": "--name='Prepare for the summer meetup' "
                + "--difficulty=hard ---------- Forwarded message --------- "
                + "From: John Doe <john@example.com> This is the body",
            },
        )

        self.jupiter("sync", "--target", "email-tasks")
        self.jupiter("gen")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Prepare for the summer meetup",
            ["Status", "Source", "Eisenhower", "Difficulty", "Project"],
        )

        assert re.search(r"Prepare for the summer meetup", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "Email Task"
        assert notion_row.attributes["Eisenhower"] == "Regular"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert notion_row.attributes["Project"] == "Work"
        assert re.search(r"[*][*]user[*][*]: John Doe", notion_row.page_content)
        assert re.search(r"[*][*]channel[*][*]: all-company", notion_row.page_content)
        assert re.search(
            r"[*][*]message[*][*]: Everybody let’s prepare for our summer meetup",
            notion_row.page_content,
        )
