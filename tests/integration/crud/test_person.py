"""Integration tests for persons."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class PersonIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for persons."""

    def test_create_person(self) -> None:
        """Creation of a person."""
        self.jupiter(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--catch-up-period",
            "weekly",
            "--birthday",
            "20 Apr",
        )

        self.go_to_notion("My Work", "Persons")

        notion_row = self.get_notion_row_in_database(
            "Mike", ["Relationship", "Catch Up Period", "Birthday"]
        )

        assert re.search(r"Mike", notion_row.title)
        assert notion_row.attributes["Relationship"] == "Friend"
        assert notion_row.attributes["Catch Up Period"] == "Weekly"
        assert notion_row.attributes["Birthday"] == "20 Apr"

        person_out = self.jupiter("person-show")

        assert re.search(r"Mike", person_out)
        assert re.search(r"[(]Friend[)]", person_out)
        assert re.search(r"Catch up Weekly", person_out)
        assert re.search(r"Birthday is 20 Apr", person_out)

    def test_update_person(self) -> None:
        """Updating a person."""
        self.jupiter(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--catch-up-period",
            "weekly",
            "--birthday",
            "20 Apr",
        )

        person_out = self.jupiter("person-show")
        person_id = extract_id_from_show_out(person_out, "Mike")

        self.jupiter(
            "person-update",
            "--id",
            person_id,
            "--name",
            "Mike Jones",
            "--birthday",
            "21 Apr",
        )

        self.go_to_notion("My Work", "Persons")

        notion_row = self.get_notion_row_in_database(
            "Mike", ["Relationship", "Catch Up Period", "Birthday"]
        )

        assert re.search(r"Mike Jones", notion_row.title)
        assert notion_row.attributes["Relationship"] == "Friend"
        assert notion_row.attributes["Catch Up Period"] == "Weekly"
        assert notion_row.attributes["Birthday"] == "21 Apr"

        person_out = self.jupiter("person-show")

        assert re.search(r"Mike Jones", person_out)
        assert re.search(r"[(]Friend[)]", person_out)
        assert re.search(r"Catch up Weekly", person_out)
        assert re.search(r"Birthday is 21 Apr", person_out)

    def test_archive_person(self) -> None:
        """Archiving a person."""
        self.jupiter(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--catch-up-period",
            "weekly",
            "--birthday",
            "20 Apr",
        )

        self.jupiter(
            "gen", "--period", "weekly", "--period", "yearly", "--target", "persons"
        )

        person_out = self.jupiter("person-show")
        person_id = extract_id_from_show_out(person_out, "Mike")

        self.jupiter("person-archive", "--id", person_id)

        self.go_to_notion("My Work", "Persons")

        assert not self.check_notion_row_exists("Mike")

        person_out = self.jupiter("person-show", "--show-archived")

        assert re.search(r"Mike", person_out)
        assert re.search(r"archived=True", person_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Catch up with Mike")
        assert not self.check_notion_row_exists("Wish happy birthday to Mike")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert re.search(r"Catch up with Mike", inbox_task_out)
        assert re.search(r"archived=True", inbox_task_out)
        assert re.search(r"Wish happy birthday to Mike", inbox_task_out)
        assert re.search(r"archived=True", inbox_task_out)

    def test_remove_person(self) -> None:
        """Archiving a person."""
        self.jupiter(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--catch-up-period",
            "weekly",
            "--birthday",
            "20 Apr",
        )

        self.jupiter(
            "gen", "--period", "weekly", "--period", "yearly", "--target", "persons"
        )

        person_out = self.jupiter("person-show")
        person_id = extract_id_from_show_out(person_out, "Mike")

        self.jupiter("person-remove", "--id", person_id)

        self.go_to_notion("My Work", "Persons")

        assert not self.check_notion_row_exists("Mike")

        person_out = self.jupiter("person-show", "--show-archived")

        assert not re.search(r"Mike", person_out)

        self.go_to_notion("My Work", "Inbox Tasks")

        assert not self.check_notion_row_exists("Catch up with Mike")
        assert not self.check_notion_row_exists("Wish happy birthday to Mike")

        inbox_task_out = self.jupiter("inbox-task-show", "--show-archived")

        assert not re.search(r"Catch up with Mike", inbox_task_out)
        assert not re.search(r"With happy birthday to Mike", inbox_task_out)

    def test_person_change_catch_up_project(self) -> None:
        """Changing the catch up project for persons tasks."""
        self.jupiter("person-change-catch-up-project", "--catch-up-project", "personal")

        person_out = self.jupiter("person-show")
        assert re.search(r"The catch up project is Personal", person_out)

        self.jupiter(
            "person-create",
            "--name",
            "Mike",
            "--relationship",
            "friend",
            "--catch-up-period",
            "weekly",
        )
        self.jupiter("gen", "--period", "weekly", "--target", "persons")

        self.go_to_notion("My Work", "Inbox Tasks", board_view="Kanban By Eisen")

        notion_row = self.get_notion_row(
            "Catch up with Mike",
            ["Project"],
        )

        assert notion_row.attributes["Project"] == "Personal"
