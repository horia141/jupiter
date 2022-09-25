"""Integration tests for vacations."""
import re

from tests.integration.infra import JupiterIntegrationTestCase


class VacationIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for vacations."""

    def test_create_vacation(self) -> None:
        """Creation of a vacation."""
        self.jupiter(
            "vacation-create",
            "--name",
            "Summer Trip",
            "--start-date",
            "2022-07-10",
            "--end-date",
            "2022-07-20",
        )

        self.go_to_notion("My Work", "Vacations")

        notion_row = self.get_notion_row_in_database(
            "Summer Trip", ["Start Date", "End Date"]
        )

        assert re.search(r"Summer Trip", notion_row.title)
        assert notion_row.attributes["Start Date"] == "July 10, 2022"
        assert notion_row.attributes["End Date"] == "July 20, 2022"

        vacation_out = self.jupiter("vacation-show")

        assert re.search(r"Summer Trip", vacation_out)
        assert re.search(r"Start at 2022-07-10", vacation_out)
        assert re.search(r"End at 2022-07-20", vacation_out)

    def test_update_vacation(self) -> None:
        """Updating a vacation."""
        vacation_id = self.jupiter_create(
            "vacation-create",
            "--name",
            "Summer Trip",
            "--start-date",
            "2022-07-10",
            "--end-date",
            "2022-07-20",
            hint="Summer Trip",
        )

        self.jupiter(
            "vacation-update",
            "--id",
            vacation_id,
            "--name",
            "Big Summer Trip",
            "--start-date",
            "2022-07-10",
            "--end-date",
            "2022-07-24",
        )

        self.go_to_notion("My Work", "Vacations")

        notion_row = self.get_notion_row_in_database(
            "Big Summer Trip", ["Start Date", "End Date"]
        )

        assert re.search(r"Big Summer Trip", notion_row.title)
        assert notion_row.attributes["Start Date"] == "July 10, 2022"
        assert notion_row.attributes["End Date"] == "July 24, 2022"

        vacation_out = self.jupiter("vacation-show")

        assert re.search(r"Big Summer Trip", vacation_out)
        assert re.search(r"Start at 2022-07-10", vacation_out)
        assert re.search(r"End at 2022-07-24", vacation_out)

    def test_archive_vacation(self) -> None:
        """Archiving a vacation."""
        vacation_id = self.jupiter_create(
            "vacation-create",
            "--name",
            "Summer Trip",
            "--start-date",
            "2022-07-10",
            "--end-date",
            "2022-07-20",
            hint="Summer Trip",
        )

        self.jupiter("vacation-archive", "--id", vacation_id)

        self.go_to_notion("My Work", "Vacations")

        assert not self.check_notion_row_exists("Summer Trip")

        vacation_out = self.jupiter("vacation-show", "--show-archived")

        assert re.search(r"Summer Trip", vacation_out)

    def test_remove_vacation(self) -> None:
        """Archiving a vacation."""
        vacation_id = self.jupiter_create(
            "vacation-create",
            "--name",
            "Summer Trip",
            "--start-date",
            "2022-07-10",
            "--end-date",
            "2022-07-20",
            hint="Summer Trip",
        )

        self.jupiter("vacation-remove", "--id", vacation_id)

        self.go_to_notion("My Work", "Vacations")

        assert not self.check_notion_row_exists("Summer Trip")

        vacation_out = self.jupiter("vacation-show", "--show-archived")

        assert not re.search(r"Summer Trip", vacation_out)
