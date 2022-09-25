"""Test case for the report functionality."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class ReportTestCase(JupiterIntegrationTestCase):
    """Test case for the report functionality."""

    def test_basic_report(self) -> None:
        """The basic report."""
        report_out = self.jupiter("report")

        assert re.search(r"Weekly as of \d\d\d\d-\d\d-\d\d", report_out)

    def test_report_with_inbox_tasks(self) -> None:
        """Reporting on inbox tasks."""
        inbox_task_1_id = self.jupiter_create(
            "inbox-task-create", "--name", "Get a cat", hint="Get a cat"
        )
        self.jupiter("inbox-task-create", "--name", "Get a dog")

        self.jupiter("inbox-task-update", "--id", inbox_task_1_id, "--status", "done")

        report_out = self.jupiter("report")

        assert re.search(r"Created\s+│\s+2\s+│\s+2\s+(│\s+0\s+)+", report_out)
        assert re.search(r"🔧\s+│\s+1\s+│\s+1\s+(│\s+0\s+)+", report_out)
        assert re.search(r"Working\s+│\s+0\s+│\s+0\s+(│\s+0\s+)+", report_out)
        assert re.search(r"⛔ Not\s+│\s+0\s+│\s+0\s+(│\s+0\s+)+", report_out)
        assert re.search(r"Done\s+│\s+1\s+│\s+1\s+(│\s+0\s+)+", report_out)

    def test_report_with_big_plan(self) -> None:
        """Reporting on big plans."""
        big_plan_1_id = self.jupiter_create(
            "big-plan-create", "--name", "Get a cat", hint="Get a cat"
        )
        self.jupiter("big-plan-create", "--name", "Get a dog")

        self.jupiter("big-plan-update", "--id", big_plan_1_id, "--status", "done")

        report_out = self.jupiter("report")

        assert re.search(
            r"""Big Plans:.+Created: 2.+Accepted: 1.+Working: 0.+Not Done: 0.+Done: 1.+Get a cat""",
            report_out,
        )

    def test_report_with_habit(self) -> None:
        """Reporting on habits."""
        self.jupiter_create(
            "habit-create", "--name", "Groom the cat", "--period", "weekly"
        )
        self.jupiter_create(
            "habit-create", "--name", "Groom the dog", "--period", "weekly"
        )
        self.jupiter("gen", "--target", "habits", "--period", "weekly")

        inbox_task_out = self.jupiter("inbox-task-show")
        inbox_task_1_id = extract_id_from_show_out(inbox_task_out, "Groom the cat")

        self.jupiter("inbox-task-update", "--id", inbox_task_1_id, "--status", "done")

        report_out = self.jupiter("report")

        assert re.search(r"Done\s+│\s+1\s+│\s+0\s+│\s+1\s+(│\s+0\s+)+", report_out)
