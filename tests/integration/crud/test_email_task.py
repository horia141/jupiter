"""Integration tests for email tasks."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class ProjectIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for Email tasks."""

    def test_update_email_task(self) -> None:
        """Updating of Email tasks."""
        self.go_to_notion("My Work", "Push Integrations", "Email")
        self.add_notion_row(
            "Time for the summer meetup",
            {
                "To Address": "horia@example.com",
                "Body": "--name='Prepare for the summer meetup' "
                + "--difficulty=hard ---------- Forwarded message ---------"
                + " From: John Doe <john@example.com> This is the body",
            },
        )

        self.jupiter("sync", "--target", "email-tasks")
        self.jupiter("gen", "--target", "email-tasks")

        email_task_out = self.jupiter("email-task-show")
        email_task_id = extract_id_from_show_out(email_task_out, "John Doe")

        self.jupiter(
            "email-task-update",
            "--id",
            email_task_id,
            "--from-address",
            "john.doe@example.com",
            "--from-name",
            "John C Doe",
            "--to-address",
            "horia.coman@example.com",
            "--subject",
            "It got cancelled",
            "--body",
            "The other body",
            "--name",
            "Cancel bookings for the summer meetup",
            "--eisen",
            "important",
            "--difficulty",
            "hard",
            "--due-date",
            "2022-05-23",
        )

        self.go_to_notion("My Work", "Push Integrations", "Email")

        notion_email_task_row = self.get_notion_row_in_database(
            "It got cancelled", ["To Address", "Body"]
        )

        assert notion_email_task_row.title == r"It got cancelled"
        assert (
            notion_email_task_row.attributes["To Address"] == "horia.coman@example.com"
        )
        assert re.search(
            "---------- Forwarded message ---------",
            notion_email_task_row.attributes["Body"],
        )
        assert re.search(
            "From: John C Doe <john.doe@example.com>",
            notion_email_task_row.attributes["Body"],
        )
        assert re.search(
            "The other body",
            notion_email_task_row.attributes["Body"],
        )
        assert re.search(
            '--name="Cancel bookings for the summer meetup"',
            notion_email_task_row.attributes["Body"],
        )
        assert re.search("--eisen=important", notion_email_task_row.attributes["Body"])
        assert re.search("--difficulty=hard", notion_email_task_row.attributes["Body"])
        assert re.search(
            "--due-date=2022-05-23", notion_email_task_row.attributes["Body"]
        )

        email_task_out = self.jupiter("email-task-show")

        assert re.search(r"John C Doe <john.doe@example.com>", email_task_out)
        assert re.search(r"to horia.coman@example.com", email_task_out)
        assert re.search(r"on 💬 It got cancelled", email_task_out)
        assert re.search(r"name=Cancel bookings for the summer meetup", email_task_out)
        assert re.search(r"Important", email_task_out)
        assert re.search(r"Hard", email_task_out)
        assert re.search(r"Due at( )+2022-05-23", email_task_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Cancel bookings for the summer meetup",
            ["Status", "Source", "Eisenhower", "Difficulty", "Due Date", "Project"],
        )

        assert re.search(r"Cancel bookings for the summer meetup", notion_row.title)
        assert notion_row.attributes["Status"] == "Accepted"
        assert notion_row.attributes["Source"] == "Email Task"
        assert notion_row.attributes["Eisenhower"] == "Important"
        assert notion_row.attributes["Difficulty"] == "Hard"
        assert re.search("May 23, 2022", notion_row.attributes["Due Date"])
        assert notion_row.attributes["Project"] == "Work"
        assert re.search(r"Summer meetup is cancelled", notion_row.page_content)

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Cancel bookings for the summer meetup", inbox_task_out)
        assert re.search(r"🔧", inbox_task_out)
        assert re.search(r"Email Task", inbox_task_out)
        assert re.search(r"Important", inbox_task_out)
        assert re.search(r"Hard", inbox_task_out)
        assert re.search(r"Due At 2022-05-23", inbox_task_out)
        assert re.search(r"In Project Work", inbox_task_out)

    def test_archive_email_task(self) -> None:
        """Archiving of Email tasks."""
        self.go_to_notion("My Work", "Push Integrations", "Email")
        self.add_notion_row(
            "Time for the summer meetup",
            {
                "To Address": "horia@example.com",
                "Body": "--name='Prepare for the summer meetup' "
                + "--difficulty=hard ---------- Forwarded message ---------"
                + " From: John Doe <john@example.com> This is the body",
            },
        )

        self.jupiter("sync", "--target", "email-tasks")

        self.jupiter("gen", "--target", "email-tasks")

        email_task_out = self.jupiter("email-task-show")
        email_task_id = extract_id_from_show_out(
            email_task_out, "Time for the summer meetup"
        )

        self.jupiter("email-task-archive", "--id", email_task_id)

        self.go_to_notion("My Work", "Push Integrations", "Email")

        assert not self.check_notion_row_exists("Time for the summer meetup")

        email_task_out = self.jupiter("email-task-show", "--show-archived")

        assert re.search(r"Time for the summer meetup", email_task_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Prepare for the summer meetup")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert re.search(r"Prepare for the summer meetup", inbox_task_out)

    def test_remove_email_task(self) -> None:
        """Removing of Email tasks."""
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

        self.jupiter("gen", "--target", "email-tasks")

        email_task_out = self.jupiter("email-task-show")
        email_task_id = extract_id_from_show_out(
            email_task_out, "Time for the summer meetup"
        )

        self.jupiter("email-task-remove", "--id", email_task_id)

        self.go_to_notion("My Work", "Push Integrations", "Email")

        assert not self.check_notion_row_exists("Time for the summer meetup")

        email_task_out = self.jupiter("email-task-show", "--show-archived")

        assert not re.search(r"Time for the summer meetup", email_task_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Prepare for the summer meetup")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert not re.search(r"Prepare for the summer meetup", inbox_task_out)

    def test_change_generation_project(self) -> None:
        """Changing the generation project for Email tasks."""
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

        self.jupiter(
            "email-task-change-generation-project", "--generation-project", "personal"
        )

        self.jupiter("gen")

        self.go_to_notion("My Work", "Inbox Tasks")

        notion_row = self.get_notion_row(
            "Prepare for the summer meetup",
            ["Project"],
        )

        assert notion_row.attributes["Project"] == "Personal"

        inbox_task_out = self.jupiter("inbox-task-show")

        assert re.search(r"Personal", inbox_task_out)
