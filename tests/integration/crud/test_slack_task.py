"""Integration tests for Slack tasks."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class ProjectIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for Slack tasks."""

    def test_update_slack_task(self) -> None:
        """Updating of Slack tasks."""
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

        slack_task_out = self.jupiter("slack-task-show")
        slack_task_id = extract_id_from_show_out(slack_task_out, "from=John Doe")

        self.jupiter(
            "slack-task-update",
            "--id",
            slack_task_id,
            "--user",
            "Johnny Doe",
            "--channel",
            "all-company-news",
            "--message",
            "Summer meetup is cancelled",
            "--name",
            "Cancel bookings for the summer meetup",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-23",
        )

        self.go_to_notion("My Work", "Push Integrations", "Slack")

        notion_slack_task_row = self.get_notion_row_in_database(
            "Johnny Doe", ["Channel", "Message", "Extra Info"]
        )

        assert notion_slack_task_row.title == r"Johnny Doe"
        assert notion_slack_task_row.attributes["Channel"] == "all-company-news"
        assert (
            notion_slack_task_row.attributes["Message"]
            == "Cancel bookings for the summer meetup"
        )
        assert re.search(
            '--name="Cancel bookings for the summer meetup"',
            notion_slack_task_row.attributes["Extra Info"],
        )
        assert re.search(
            "--eisen=important", notion_slack_task_row.attributes["Extra Info"]
        )
        assert re.search(
            "--difficulty=hard", notion_slack_task_row.attributes["Extra Info"]
        )
        assert re.search(
            "--due-date=2022-05-23", notion_slack_task_row.attributes["Extra Info"]
        )

        slack_task_out = self.jupiter("slack-task-show")

        assert re.search(r"from=Johnny Doe", slack_task_out)
        assert re.search(r"in-channel=all-company-news", slack_task_out)
        assert re.search(
            r"message=Cancel bookings for the summer meetup", slack_task_out
        )
        assert re.search(r"name=Cancel bookings for the summer meetup", slack_task_out)
        assert re.search(r"eisen=Important", slack_task_out)
        assert re.search(r"difficulty=Hard", slack_task_out)
        assert re.search(r"due-date=2022-05-23", slack_task_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Cancel bookings for the summer meetup",
            ["Status", "Source", "Eisenhower", "Difficulty", "Due Date", "Project"],
        )

        assert re.search(r"Cancel bookings for the summer meetup", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "Slack Task"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert re.search("May 23, 2022", notion_row.attributes["Due Date"])
        assert notion_row.attributes["Project"] == "Work"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Cancel bookings for the summer meetup", inbox_task_out)
        assert re.search(r"status=Accepted", inbox_task_out)
        assert re.search(r"source=Slack Task", inbox_task_out)
        assert re.search(r"eisen=Important", inbox_task_out)
        assert re.search(r"difficulty=Hard", inbox_task_out)
        assert re.search(r"due-date=2022-05-23", inbox_task_out)
        assert re.search(r"project=Work", inbox_task_out)

    def test_archive_slack_task(self) -> None:
        """Archiving of Slack tasks."""
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

        slack_task_out = self.jupiter("slack-task-show")
        slack_task_id = extract_id_from_show_out(slack_task_out, "from=John Doe")

        self.jupiter("slack-task-archive", "--id", slack_task_id)

        self.go_to_notion("My Work", "Push Integrations", "Slack")

        assert not self.check_notion_row_exists("Johnny Doe")

        slack_task_out = self.jupiter("slack-task-show", "--show-archived")

        assert re.search(
            r"message=Everybody let's prepare for our summer meetup", slack_task_out
        )
        assert re.search(r"archived=True", slack_task_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Prepare for the summer meetup")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert re.search(r"Prepare for the summer meetup", inbox_task_out)
        assert re.search(r"archived=True", inbox_task_out)

    def test_remove_slack_task(self) -> None:
        """Removing of Slack tasks."""
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

        slack_task_out = self.jupiter("slack-task-show")
        slack_task_id = extract_id_from_show_out(slack_task_out, "from=John Doe")

        self.jupiter("slack-task-remove", "--id", slack_task_id)

        self.go_to_notion("My Work", "Push Integrations", "Slack")

        assert not self.check_notion_row_exists("Johnny Doe")

        slack_task_out = self.jupiter("slack-task-show", "--show-archived")

        assert not re.search(
            r"message=Everybody let’s prepare for our summer meetup", slack_task_out
        )

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Prepare for the summer meetup")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert not re.search(r"Prepare for the summer meetup", inbox_task_out)

    def test_change_generation_project(self) -> None:
        """Changing the generation project for Slack tasks."""
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

        self.jupiter(
            "slack-task-change-generation-project", "--generation-project", "personal"
        )

        self.jupiter("gen")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Prepare for the summer meetup",
            ["Project"],
        )

        assert notion_row.attributes["Project"] == "Personal"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"project=Personal", inbox_task_out)
