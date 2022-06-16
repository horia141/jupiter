"""Integration tests for metrics."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class MetricIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for metrics."""

    def test_create_metric(self) -> None:
        """Creation of a metric."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
            "--collection-period",
            "weekly",
        )

        self.go_to_notion("My Work", "Metrics", "Weight")

        metric_out = self.jupiter("metric-show")

        assert re.search(r"weight:", metric_out)
        assert re.search(r"Weight", metric_out)
        assert re.search(r"@Weekly", metric_out)
        assert re.search(r"eisen=Regular", metric_out)

    def test_update_metric(self) -> None:
        """Update of a metric."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
            "--collection-period",
            "weekly",
        )

        self.jupiter(
            "metric-update",
            "--metric",
            "weight",
            "--name",
            "Weight Big",
            "--collection-period",
            "monthly",
            "--collection-eisen",
            "important",
            "--collection-difficulty",
            "hard",
        )

        self.go_to_notion("My Work", "Metrics", "Weight Big")

        metric_out = self.jupiter("metric-show")

        assert re.search(r"weight:", metric_out)
        assert re.search(r"Weight Big", metric_out)
        assert re.search(r"@Monthly", metric_out)
        assert re.search(r"eisen=Important", metric_out)
        assert re.search(r"difficulty=Hard", metric_out)

    def test_archive_metric(self) -> None:
        """Archive of a metric."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
            "--collection-period",
            "weekly",
        )

        self.jupiter(
            "metric-entry-create",
            "--metric",
            "weight",
            "--collection-time",
            "2022-05-21",
            "--value",
            "83.2",
            "--notes",
            "A decent day",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "metrics")

        self.jupiter("metric-archive", "--metric", "weight")

        self.go_to_notion("My Work", "Metrics")

        assert not self.check_notion_row_exists("Weight")

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Collect value for metric Weight")

        metric_out = self.jupiter("metric-show", "--show-archived")

        assert re.search(r"weight:", metric_out)
        assert re.search(r"Weight", metric_out)
        assert re.search(r"@Weekly", metric_out)
        assert re.search(r"eisen=Regular", metric_out)
        assert re.search(r"archived=True", metric_out)

        assert re.search(r"2022-05-21", metric_out)
        assert re.search(r"notes=A decent day", metric_out)
        assert re.search(r"val=83.2", metric_out)
        assert re.search(r"archived=True", metric_out)

        assert re.search(r"Collect value for metric Weight", metric_out)
        assert re.search(r"archived=True", metric_out)

    def test_remove_metric(self) -> None:
        """Remove of a metric."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
            "--collection-period",
            "weekly",
        )

        self.jupiter(
            "metric-entry-create",
            "--metric",
            "weight",
            "--collection-time",
            "2022-05-21",
            "--value",
            "83.2",
            "--notes",
            "A decent day",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "metrics")

        self.jupiter("metric-remove", "--metric", "weight")

        self.go_to_notion("My Work", "Metrics")

        assert not self.check_notion_row_exists("Weight")

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Collect value for metric Weight")

        metric_out = self.jupiter("metric-show", "--show-archived")

        assert not re.search(r"weight:", metric_out)
        assert not re.search(r"Weight", metric_out)

        assert not re.search(r"2022-05-21", metric_out)

        assert not re.search(r"Collect value for metric Weight", metric_out)

    def test_create_metric_entry(self) -> None:
        """Creation of a metric entry."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
        )

        self.jupiter(
            "metric-entry-create",
            "--metric",
            "weight",
            "--collection-time",
            "2022-05-21",
            "--value",
            "83.2",
            "--notes",
            "A decent day",
        )

        self.go_to_notion("My Work", "Metrics", "Weight")

        notion_row = self.get_notion_row_in_database(
            "A decent day",
            ["Collection Time", "Value"],
        )

        assert re.search(r"A decent day", notion_row.title)
        assert re.search(r"May 21, 2022", notion_row.attributes["Collection Time"])
        assert re.search(r"83.2", notion_row.attributes["Value"])

        metric_out = self.jupiter("metric-show")

        assert re.search(r"2022-05-21", metric_out)
        assert re.search(r"notes=A decent day", metric_out)
        assert re.search(r"val=83.2", metric_out)

    def test_update_metric_entry(self) -> None:
        """Update of a metric entry."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
        )

        self.jupiter(
            "metric-entry-create",
            "--metric",
            "weight",
            "--collection-time",
            "2022-05-21",
            "--value",
            "83.2",
            "--notes",
            "A decent day",
        )

        metric_out = self.jupiter("metric-show")
        metric_entry_id = extract_id_from_show_out(metric_out, "2022-05-21")

        self.jupiter(
            "metric-entry-update",
            "--id",
            metric_entry_id,
            "--collection-time",
            "2022-05-22",
            "--value",
            "83.5",
            "--notes",
            "A better day",
        )

        self.go_to_notion("My Work", "Metrics", "Weight")

        notion_row = self.get_notion_row_in_database(
            "A better day",
            ["Collection Time", "Value"],
        )

        assert re.search(r"A better day", notion_row.title)
        assert re.search(r"May 22, 2022", notion_row.attributes["Collection Time"])
        assert re.search(r"83.5", notion_row.attributes["Value"])

        metric_out = self.jupiter("metric-show")

        assert re.search(r"2022-05-22", metric_out)
        assert re.search(r"notes=A better day", metric_out)
        assert re.search(r"val=83.5", metric_out)

    def test_archive_metric_entry(self) -> None:
        """Archive of a metric entry."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
        )

        self.jupiter(
            "metric-entry-create",
            "--metric",
            "weight",
            "--collection-time",
            "2022-05-21",
            "--value",
            "83.2",
            "--notes",
            "A decent day",
        )

        metric_out = self.jupiter("metric-show")
        metric_entry_id = extract_id_from_show_out(metric_out, "2022-05-21")

        self.jupiter("metric-entry-archive", "--id", metric_entry_id)

        self.go_to_notion("My Work", "Metrics", "Weight")

        assert not self.check_notion_row_exists("A decent day")

        metric_out = self.jupiter("metric-show", "--show-archived")

        assert re.search(r"2022-05-21", metric_out)
        assert re.search(r"notes=A decent day", metric_out)
        assert re.search(r"val=83.5", metric_out)

    def test_remove_metric_entry(self) -> None:
        """Remove of a metric entry."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
        )

        self.jupiter(
            "metric-entry-create",
            "--metric",
            "weight",
            "--collection-time",
            "2022-05-21",
            "--value",
            "83.2",
            "--notes",
            "A decent day",
        )

        metric_out = self.jupiter("metric-show")
        metric_entry_id = extract_id_from_show_out(metric_out, "2022-05-21")

        self.jupiter("metric-entry-remove", "--id", metric_entry_id)

        self.go_to_notion("My Work", "Metrics", "Weight")

        assert not self.check_notion_row_exists("A better day")

        metric_out = self.jupiter("metric-show", "--show-archived")

        assert not re.search(r"2022-05-22", metric_out)

    def test_change_collection_project(self) -> None:
        """Change the collection project of a metric."""
        self.jupiter(
            "metric-create",
            "--metric",
            "weight",
            "--name",
            "Weight",
            "--unit",
            "weight",
            "--collection-period",
            "weekly",
        )

        self.jupiter("gen", "--period", "weekly", "--target", "metrics")

        self.go_to_notion("My Work", "Inbox Tasks")

        assert self.get_notion_row("Collect value for metric Weight", []) is not None

        self.jupiter(
            "metric-change-collection-project", "--collection-project", "personal"
        )

        notion_row = self.get_notion_row(
            "Collect value for metric Weight",
            ["Project"],
        )

        assert notion_row.attributes["Project"] == "Personal"

        metric_out = self.jupiter("metric-show")

        assert re.search("The collection project is Personal", metric_out)
