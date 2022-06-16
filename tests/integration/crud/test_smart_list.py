"""Integration tests for smart lists."""
import re

from tests.integration.infra import JupiterIntegrationTestCase, extract_id_from_show_out


class SmartListIntegrationTestCase(JupiterIntegrationTestCase):
    """Integration tests for smart lists."""

    def test_create_smart_list(self) -> None:
        """Create a smart list."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        smart_list_out = self.jupiter("smart-list-show")

        assert re.search(r"fantasy:", smart_list_out)
        assert re.search(r"Fantasy Books", smart_list_out)

    def test_update_smart_list(self) -> None:
        """Updating a smart list."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-update",
            "--smart-list",
            "fantasy",
            "--name",
            "Best Fantasy Books",
        )

        self.go_to_notion("My Work", "Smart Lists", "Best Fantasy Books")

        smart_list_out = self.jupiter("smart-list-show")

        assert re.search(r"fantasy:", smart_list_out)
        assert re.search(r"Best Fantasy Books", smart_list_out)

    def test_archive_smart_list(self) -> None:
        """Archiving a smart list."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "series",
            "--tag",
            "highfantasy",
        )

        self.jupiter("smart-list-archive", "--smart-list", "fantasy")

        self.go_to_notion("My Work", "Smart Lists")

        assert not self.check_notion_row_exists("Fantasy Books")

        smart_list_out = self.jupiter("smart-list-show", "--show-archived")

        assert re.search(r"fantasy:", smart_list_out)
        assert re.search(r"archived=True", smart_list_out)
        assert re.search(r"The Lord Of The Rings", smart_list_out)
        assert re.search(r"archived=True", smart_list_out)

    def test_remove_smart_list(self) -> None:
        """Removing a smart list."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "series",
            "--tag",
            "highfantasy",
        )

        self.jupiter("smart-list-remove", "--smart-list", "fantasy")

        self.go_to_notion("My Work", "Smart Lists")

        assert not self.check_notion_row_exists("Fantasy Books")

        smart_list_out = self.jupiter("smart-list-show", "--show-archived")

        assert not re.search(r"fantasy:", smart_list_out)
        assert not re.search(r"The Lord Of The Rings", smart_list_out)

    def test_create_smart_list_item(self) -> None:
        """Creating a smart list item."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "series",
            "--tag",
            "highfantasy",
        )

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        notion_row = self.get_notion_row_in_database("The Lord Of The Rings", ["Tags"])

        assert notion_row.title == "The Lord Of The Rings"
        assert re.search(r"series", notion_row.attributes["Tags"])
        assert re.search(r"highfantasy", notion_row.attributes["Tags"])

        smart_list_out = self.jupiter("smart-list-show")

        assert re.search(r"The Lord Of The Rings", smart_list_out)
        assert re.search(r"#series", smart_list_out)
        assert re.search(r"#highfantasy", smart_list_out)

    def test_update_smart_list_item(self) -> None:
        """Updating a smart list item."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "series",
            "--tag",
            "highfantasy",
        )

        smart_list_out = self.jupiter("smart-list-show")
        smart_list_item_id = extract_id_from_show_out(
            smart_list_out, "The Lord Of The Rings"
        )

        self.jupiter(
            "smart-list-item-update",
            "--id",
            smart_list_item_id,
            "--name",
            "The Lord Of The Rings Series",
            "--tag",
            "highfantasy",
            "--tag",
            "modern",
        )

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        notion_row = self.get_notion_row_in_database(
            "The Lord Of The Rings Series", ["Tags"]
        )

        assert notion_row.title == "The Lord Of The Rings Series"
        assert not re.search(r"series", notion_row.attributes["Tags"])
        assert re.search(r"highfantasy", notion_row.attributes["Tags"])
        assert re.search(r"modern", notion_row.attributes["Tags"])

        smart_list_out = self.jupiter("smart-list-show")

        assert re.search(r"The Lord Of The Rings", smart_list_out)
        assert re.search(r"#highfantasy", smart_list_out)
        assert re.search(r"#modern", smart_list_out)

    def test_archive_smart_list_item(self) -> None:
        """Archiving a smart list item."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "series",
            "--tag",
            "highfantasy",
        )

        smart_list_out = self.jupiter("smart-list-show")
        smart_list_item_id = extract_id_from_show_out(
            smart_list_out, "The Lord Of The Rings"
        )

        self.jupiter("smart-list-item-archive", "--id", smart_list_item_id)

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        assert not self.check_notion_row_exists("The Lord Of The Rings")

        smart_list_out = self.jupiter("smart-list-show", "--show-archived")

        assert re.search(r"The Lord Of The Rings", smart_list_out)
        assert re.search(r"archived=True", smart_list_out)

    def test_remove_smart_list_item(self) -> None:
        """Remocing a smart list item."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "series",
            "--tag",
            "highfantasy",
        )

        smart_list_out = self.jupiter("smart-list-show")
        smart_list_item_id = extract_id_from_show_out(
            smart_list_out, "The Lord Of The Rings"
        )

        self.jupiter("smart-list-item-remove", "--id", smart_list_item_id)

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        assert not self.check_notion_row_exists("The Lord Of The Rings")

        smart_list_out = self.jupiter("smart-list-show", "--show-archived")

        assert not re.search(r"The Lord Of The Rings", smart_list_out)

    def test_create_smart_list_tag(self) -> None:
        """Creating a smart list tag."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-tag-create", "--smart-list", "fantasy", "--name", "highfantasy"
        )

        # self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        smart_list_out = self.jupiter("smart-list-show")

        assert re.search(r"#highfantasy", smart_list_out)

    def test_update_smart_list_tag(self) -> None:
        """Updating a smart list tag."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-tag-create", "--smart-list", "fantasy", "--name", "highfantasy"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "highfantasy",
        )

        smart_list_out = self.jupiter("smart-list-show")
        smart_list_tag_id = extract_id_from_show_out(smart_list_out, "#highfantasy")

        self.jupiter(
            "smart-list-tag-update",
            "--id",
            smart_list_tag_id,
            "--name",
            "thehighfantasy",
        )

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        notion_row = self.get_notion_row_in_database("The Lord Of The Rings", ["Tags"])

        assert notion_row.title == "The Lord Of The Rings"
        assert re.search(r"thehighfantasy", notion_row.attributes["Tags"])

        smart_list_out = self.jupiter("smart-list-show")

        assert re.search(r"The Lord Of The Rings", smart_list_out)
        assert re.search(r"#thehighfantasy", smart_list_out)

    def test_archive_smart_list_tag(self) -> None:
        """Archiving a smart list tag."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-tag-create", "--smart-list", "fantasy", "--name", "highfantasy"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "highfantasy",
        )

        smart_list_out = self.jupiter("smart-list-show")
        smart_list_tag_id = extract_id_from_show_out(smart_list_out, "#highfantasy")

        self.jupiter("smart-list-tag-archive", "--id", smart_list_tag_id)

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        notion_row = self.get_notion_row_in_database("The Lord Of The Rings", ["Tags"])

        assert notion_row.title == "The Lord Of The Rings"
        assert not re.search(r"highfantasy", notion_row.attributes["Tags"])

        smart_list_out = self.jupiter("smart-list-show", "--show-archived")

        assert re.search(r"#highfantasy", smart_list_out)

    def test_remove_smart_list_tag(self) -> None:
        """Removing a smart list tag."""
        self.jupiter(
            "smart-list-create", "--smart-list", "fantasy", "--name", "Fantasy Books"
        )

        self.jupiter(
            "smart-list-tag-create", "--smart-list", "fantasy", "--name", "highfantasy"
        )

        self.jupiter(
            "smart-list-item-create",
            "--smart-list",
            "fantasy",
            "--name",
            "The Lord Of The Rings",
            "--tag",
            "highfantasy",
        )

        smart_list_out = self.jupiter("smart-list-show")
        smart_list_tag_id = extract_id_from_show_out(smart_list_out, "#highfantasy")

        self.jupiter("smart-list-tag-remove", "--id", smart_list_tag_id)

        self.go_to_notion("My Work", "Smart Lists", "Fantasy Books")

        notion_row = self.get_notion_row_in_database("The Lord Of The Rings", ["Tags"])

        assert notion_row.title == "The Lord Of The Rings"
        assert not re.search(r"highfantasy", notion_row.attributes["Tags"])

        smart_list_out = self.jupiter("smart-list-show", "--show-archived")

        assert not re.search(r"#thehighfantasy", smart_list_out)
