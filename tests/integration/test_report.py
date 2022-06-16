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
        self.jupiter("inbox-task-create", "--name", "Get a cat")
        self.jupiter("inbox-task-create", "--name", "Get a dog")
        inbox_task_out = self.jupiter("inbox-task-show")
        inbox_task_1_id = extract_id_from_show_out(inbox_task_out, "Get a cat")

        self.jupiter("inbox-task-update", "--id", inbox_task_1_id, "--status", "done")

        report_out = self.jupiter("report")

        assert re.search(
            "Created: 2 [(]2 from User[)] "
            + "[(]0 from Habit[)] "
            + "[(]0 from Chore[)] "
            + "[(]0 from Big Plan[)] "
            + "[(]0 from Metric[)] "
            + "[(]0 from Person Catch Up[)] "
            + "[(]0 from Person Birthday[)] "
            + "[(]0 from Slack Task[)]",
            report_out,
        )
        assert re.search(
            "Accepted: 1 [(]1 from User[)]"
            + " [(]0 from Habit[)]"
            + " [(]0 from Chore[)]"
            + " [(]0 from Big Plan[)]"
            + " [(]0 from Metric[)]"
            + " [(]0 from Person Catch Up[)]"
            + " [(]0 from Person Birthday[)]"
            + " [(]0 from Slack Task[)]",
            report_out,
        )
        assert re.search(
            "Working: 0 [(]0 from User[)]"
            + " [(]0 from Habit[)]"
            + " [(]0 from Chore[)]"
            + " [(]0 from Big Plan[)]"
            + " [(]0 from Metric[)]"
            + " [(]0 from Person Catch Up[)]"
            + " [(]0 from Person Birthday[)]"
            + " [(]0 from Slack Task[)]",
            report_out,
        )
        assert re.search(
            "Not Done: 0 [(]0 from User[)]"
            + " [(]0 from Habit[)]"
            + " [(]0 from Chore[)]"
            + " [(]0 from Big Plan[)]"
            + " [(]0 from Metric[)]"
            + " [(]0 from Person Catch Up[)]"
            + " [(]0 from Person Birthday[)]"
            + " [(]0 from Slack Task[)]",
            report_out,
        )
        assert re.search(
            "Done: 1 [(]1 from User[)]"
            + " [(]0 from Habit[)]"
            + " [(]0 from Chore[)]"
            + " [(]0 from Big Plan[)]"
            + " [(]0 from Metric[)]"
            + " [(]0 from Person Catch Up[)]"
            + " [(]0 from Person Birthday[)]"
            + " [(]0 from Slack Task[)]",
            report_out,
        )

    def test_report_with_big_plan(self) -> None:
        """Reporting on big plans."""
        self.jupiter("big-plan-create", "--name", "Get a cat")
        self.jupiter("big-plan-create", "--name", "Get a dog")
        big_plan_out = self.jupiter("big-plan-show")
        big_plan_1_id = extract_id_from_show_out(big_plan_out, "Get a cat")

        self.jupiter("big-plan-update", "--id", big_plan_1_id, "--status", "done")

        report_out = self.jupiter("report")

        assert re.search(
            r"""Big Plans:[ ]+[ ]+Created: 2[ ]+Accepted: 1[ ]+Working: 0[ ]+Not Done: 0[ ]+Done: 1[ ]+- Get a cat""",
            report_out,
        )

    def test_report_with_habit(self) -> None:
        """Reporting on habits."""
        self.jupiter("habit-create", "--name", "Groom the cat", "--period", "weekly")
        self.jupiter("habit-create", "--name", "Groom the dog", "--period", "weekly")
        self.jupiter("gen", "--target", "habits", "--period", "weekly")

        inbox_task_out = self.jupiter("inbox-task-show")
        inbox_task_1_id = extract_id_from_show_out(inbox_task_out, "Groom the cat")

        self.jupiter("inbox-task-update", "--id", inbox_task_1_id, "--status", "done")

        report_out = self.jupiter("report")

        assert re.search(r"Done: 1.*[(]1 from Habit[)]", report_out)
        assert re.search("Groom the cat[ ]*=> X", report_out)
        assert re.search("Groom the dog[ ]*=> ?", report_out)
