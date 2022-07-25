"""The core integration tests infrastructure where all the magic happens."""
import json
import os
import pdb
import re
import subprocess
import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, ClassVar, Optional, Union, List, cast, Sequence

import dotenv
import pendulum
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


@dataclass(frozen=True)
class ExtractedNotionRow:
    """A Notion row extracted very briefly via Selenium scans."""

    title: str
    attributes: Dict[str, str]
    page_content: str


@dataclass(frozen=True)
class NotionSelect:
    """A way of telling Notion that a particular field should be completed as a select not a free-form text."""

    value: str


@dataclass(frozen=True)
class BetterMatch:
    """A way of telling Notion that a particular field should be extracted more carefully."""

    key: str
    value: str


class JupiterBasicIntegrationTestCase(unittest.TestCase):
    """A base class for Jupiter integration test cases which don't assume a preexisting workspace."""

    _MAX_WAIT_TIME_SECONDS: ClassVar[int] = 10

    _driver: ClassVar[Optional[WebDriver]]
    _root_path: ClassVar[Optional[Path]]
    _cache_path: ClassVar[Optional[Path]]
    _tmp_file: ClassVar[Optional[Path]]
    _space_id: ClassVar[Optional[str]]
    _token_v2: ClassVar[Optional[str]]
    _notion_api_token: ClassVar[Optional[str]]

    @classmethod
    def setUpClass(cls) -> None:
        """Set things up for the test suite."""
        cls._root_path = Path(os.path.realpath(__file__)).parent.parent.parent
        config_path = cls._root_path / "tests" / "integration" / "Config.test"
        dotenv.load_dotenv(dotenv_path=config_path, verbose=True)

        notion_user = os.getenv("NOTION_USER")
        notion_pass = os.getenv("NOTION_PASS")
        notion_api_token = os.getenv("NOTION_API_TOKEN")

        cls._cache_path = cls._root_path / ".build-cache" / "itest"

        webdriver_cache_path = cls._cache_path / "webdrivers"

        chrome_data_path = cls._cache_path / "chrome-data"

        options = Options()
        options.add_argument(f"--user-data-dir={chrome_data_path}")
        cls._driver = WebDriver(
            options=options,
            service=Service(ChromeDriverManager(path=webdriver_cache_path).install()),
        )
        cls._driver.implicitly_wait(
            JupiterBasicIntegrationTestCase._MAX_WAIT_TIME_SECONDS
        )  # seconds

        # Launch the website

        cls._driver.get("https://notion.so/login")

        notion_space_data_path = cls._cache_path / "space-data.json"

        token_v2: str
        space_id: str
        if not notion_space_data_path.is_file():
            email_field = cls._driver.find_element(By.ID, "notion-email-input-1")
            email_field.send_keys(notion_user)
            email_button = cls._driver.find_element(
                by=By.XPATH,
                value="/html/body//div[@class[contains(.,'notion-focusable')]"
                + " and @role[contains(., 'button')] and contains(., 'Continue with email')]",
            )
            email_button.click()
            pass_field = cls._driver.find_element(By.ID, "notion-password-input-2")
            pass_field.send_keys(notion_pass)
            pass_button = cls._driver.find_element(
                by=By.XPATH,
                value="/html/body//div[@class[contains(.,'notion-focusable')]"
                + " and @role[contains(., 'button')] and contains(., 'Continue with password')]",
            )
            pass_button.click()
            cls._driver.find_element(
                By.XPATH, "/html/body//span[contains(., 'Have a question?')]"
            )

            settings_button = cls._driver.find_element(
                By.XPATH,
                "/html/body//div[@class[contains(.,'notion-focusable')]"
                + " and @role[contains(., 'button')] and contains(., 'Settings & Members')]",
            )
            settings_button.click()
            security_button = cls._driver.find_element(
                By.XPATH,
                "/html/body//div[@class[contains(.,'notion-focusable')]"
                + " and @role[contains(., 'button')] and contains(., 'Security')]",
            )
            security_button.click()

            time.sleep(1)
            space_id_text = cls._driver.find_element(
                By.XPATH,
                "/html/body//a[@class[contains(., 'notion-link')] and not(@href)]",
            )

            space_id = space_id_text.text
            token_v2 = cls._driver.get_cookie("token_v2")["value"]

            notion_space_data = {"token_v2": token_v2, "space_id": space_id}
            with notion_space_data_path.open("w") as notion_space_data_file:
                json.dump(notion_space_data, notion_space_data_file)
        else:
            with notion_space_data_path.open("r") as notion_space_data_file:
                notion_space_data = json.load(notion_space_data_file)
            token_v2 = notion_space_data["token_v2"]
            space_id = notion_space_data["space_id"]

        cls._tmp_file = cls._cache_path / "jupiter.sqlite"
        cls._space_id = space_id
        cls._token_v2 = token_v2
        cls._notion_api_token = notion_api_token

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down things."""
        if cls._driver is not None:
            cls._driver.close()

    @classmethod
    def jupiter(cls, *command: str, sqlite_db_path: Optional[Path] = None) -> str:
        """Run the jupiter command."""
        if not cls._root_path:
            raise Exception("No root path")

        real_sqlite_db_path = sqlite_db_path or cls._tmp_file
        new_env = dict(
            os.environ,
            SQLITE_DB_URL=f"sqlite+pysqlite:///{real_sqlite_db_path}",
        )
        if os.getenv("COLLECT_COVERAGE") == "TRUE":
            coverage_config_path = cls._root_path / "scripts" / "coveragerc"
            new_env["COVERAGE_PROCESS_START"] = str(coverage_config_path)

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "jupiter.jupiter",
                    "--verbose",
                    *command,
                ],
                stderr=sys.stderr,
                stdout=subprocess.PIPE,
                check=True,
                env=new_env,
            )

            return result.stdout.decode("utf-8").replace("\n", " ").replace("’", "'")
        except subprocess.CalledProcessError as err:
            raise AssertionError(
                f"Invoking {' '.join(command)} failed. Stdout: {err.stdout} Stderr: {err.stderr}"
            ) from err

    @classmethod
    def go_to_notion(
        cls, root_page: str, *subpages: str, board_view: Optional[str] = None
    ) -> None:
        """Go to a particular Notion page via following navigation and pick a board too."""
        root_page_button = cls.driver().find_element(
            by=By.XPATH,
            value=f"//div[@data-block-id and contains(., '{root_page}')]//a",
        )
        root_page_button.click()

        for subpage in subpages:
            sub_page_button = cls.driver().find_element(
                by=By.XPATH,
                value="//div[@class='notion-page-content']//div[(@class='notion-selectable "
                + "notion-collection_view_page-block' or @class='notion-selectable notion-page-block')"
                + f" and contains(., '{subpage}')]",
            )
            sub_page_button.click()

        if board_view is not None:
            all_board_button = cls.driver().find_element(
                By.XPATH,
                "//*[local-name()='svg' and (@class='collectionBoard' "
                + "or @class='collectionTimeline' or @class='collectionTable')]",
            )
            all_board_button.click()
            board_button = cls.driver().find_element(
                By.XPATH,
                f"//div[@class='notion-focusable']//div[contains(., '{board_view}')]",
            )
            board_button.click()
            time.sleep(
                1
            )  # This is stupid! It just needs to get the panel to dissapear. Just timeouts worked well.

    @classmethod
    def add_notion_row(
        cls,
        title: str,
        fields: Dict[
            str,
            Union[bool, float, str, NotionSelect, List[NotionSelect], pendulum.Date],
        ],
    ) -> None:
        """Add a Notion row to the currently visible board."""
        add_row_button = cls.driver().find_element(
            By.XPATH, "/html/body//div[@class='notion-collection-view-item-add']"
        )
        add_row_button.click()

        # Try to click on the `X more properties` field.
        cls.driver().implicitly_wait(0)
        try:
            more_properties_button = WebDriverWait(cls.driver(), 0.1).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='notion-focusable']//div[contains(., 'more properties')]",
                    )
                )
            )
            more_properties_button.click()
        except (NoSuchElementException, TimeoutException):
            # Small chance page hasn't loaded. But bigger chance button has already been pressed.
            pass
        cls.driver().implicitly_wait(
            JupiterBasicIntegrationTestCase._MAX_WAIT_TIME_SECONDS
        )  # seconds

        for field_name, field_value in fields.items():
            # Complete all
            if isinstance(field_value, bool):
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@style='display: flex; flex-direction: column;' and "
                    + f"contains(., '{field_name}')]//*[local-name()='svg' and @class='checkboxSquare']",
                )
                if field_value is True:
                    field_big_container.click()
            elif isinstance(field_value, float):
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@style='display: flex; flex-direction: column;' and "
                    + f"contains(., '{field_name}')]//div[@class='notion-focusable' and contains(., 'Empty')]",
                )
                cls.driver().execute_script("arguments[0].click()", field_big_container)
                text_input = cls.driver().find_element(By.XPATH, "//input")
                text_input.send_keys(field_value)
                text_input.send_keys(Keys.ENTER)
            elif isinstance(field_value, str):
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    f"//div[@style='display: flex; flex-direction: column;' and "
                    f"contains(., '{field_name}')]//div[@class='notion-focusable' and contains(., 'Empty')]",
                )
                cls.driver().execute_script("arguments[0].click()", field_big_container)
                text_input = cls.driver().find_element(
                    By.XPATH,
                    "//div[contains(@style, 'flex-direction: column-reverse;')]//div[@class='notranslate' "
                    + "and @data-content-editable-leaf='true' and contains(@style, 'caret-color: rgb(55, 53, 47);')]",
                )
                text_input.send_keys(field_value)
                text_input.send_keys(Keys.ENTER)
            elif isinstance(field_value, NotionSelect):
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@style='display: flex; flex-direction: column;' and "
                    + f"contains(., '{field_name}')]//div[@class='notion-focusable' and contains(., 'Empty')]",
                )
                cls.driver().execute_script("arguments[0].click()", field_big_container)
                select_input = cls.driver().find_element(
                    By.XPATH,
                    f"//div[@style='display: flex;']//div[contains(., '{field_value.value}')]",
                )
                select_input.click()
            elif isinstance(field_value, List):
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@style='display: flex; flex-direction: column;' and "
                    + f"contains(., '{field_name}')]//div[@class='notion-focusable' and contains(., 'Empty')]",
                )
                cls.driver().execute_script("arguments[0].click()", field_big_container)

                text_input = None
                for field_subvalue in field_value:
                    text_input = cls.driver().find_element(By.XPATH, "//input")
                    text_input.send_keys(cast(NotionSelect, field_subvalue).value)
                    text_input.send_keys(Keys.ENTER)
                if text_input:
                    text_input.send_keys(Keys.ESCAPE)
            elif isinstance(field_value, pendulum.Date):
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@style='display: flex; flex-direction: column;' and "
                    + f"contains(., '{field_name}')]//div[@class='notion-focusable' and contains(., 'Empty')]",
                )
                cls.driver().execute_script("arguments[0].click()", field_big_container)
                date_input = cls.driver().find_element(
                    By.XPATH, "//input[@type='text']"
                )
                date_input.click()
                for _ in range(1, 20):
                    date_input.send_keys(Keys.BACKSPACE)
                date_input.send_keys(field_value.to_formatted_date_string())
                date_input.send_keys(Keys.ENTER)
                date_input.send_keys(Keys.ESCAPE)
            else:
                raise Exception(f"Unhandled Notion-side value <{field_value}>")

        title_edit = cls.driver().find_element(
            By.XPATH,
            "//div[@class='notion-selectable notion-page-block']/div[@contenteditable='true']",
        )
        title_edit.send_keys(title)
        title_edit.send_keys(Keys.ESCAPE)  # Get out of the edit flow!

        # Eventual consistency is a PITA
        time.sleep(1)

    @classmethod
    def get_notion_row_in_database(
        cls, title: str, fields: List[str]
    ) -> ExtractedNotionRow:
        """Get a Notion row from the currently visible database table."""
        return cls.get_notion_row(title, fields, in_database_view=True)

    @classmethod
    def get_notion_row(
        cls,
        title: str,
        fields: Sequence[Union[str, BetterMatch]],
        in_database_view: bool = False,
    ) -> ExtractedNotionRow:
        """Get a Notion row from the currently visible board."""
        full_notion_row = cls.driver().find_element(
            By.XPATH,
            f"//div[@data-block-id and contains(@class, 'notion-collection-item') and contains(., '{title}')]",
        )

        if not in_database_view:
            full_notion_row.click()
        else:
            action = ActionChains(cls.driver())
            action.move_to_element(full_notion_row).perform()
            # Like it so much, I'll do it twice!
            action = ActionChains(cls.driver())
            action.move_to_element(full_notion_row).perform()
            open_button = cls.driver().find_element(
                By.XPATH,
                "//div[contains(@style, 'font-size: 12px;') and contains(., 'Open')]",
            )
            open_button.click()

        time.sleep(1) # Animation be animating in the latest Notion

        attributes: Dict[str, str] = {}

        for field_matcher in fields:
            if isinstance(field_matcher, str):
                field_name = field_matcher
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@class='notion-scroller vertical']//div[@style='display: flex; flex-direction: column;' "
                    + f" and contains(., '{field_name}') and not(contains(., '{field_name} Id'))]",
                )
            else:
                field_name = field_matcher.key
                field_value = field_matcher.value
                field_big_container = cls.driver().find_element(
                    By.XPATH,
                    "//div[@class='notion-scroller vertical']//div[@style='display: flex; flex-direction: column;'"
                    + f" and contains(., '{field_name}') and contains(., '{field_value}') "
                    + f"and not(contains(., '{field_name} Id'))]",
                )
            field_raw_text = field_big_container.text
            if not field_raw_text:
                raise AssertionError(
                    f"Field {field_name} could not be parsed with value '{field_raw_text}'"
                )
            field_values = field_raw_text.split("\n")
            if len(field_values) < 2:
                raise AssertionError(
                    f"Field {field_name} could not be parsed with value '{field_raw_text}'"
                )
            field_value = " ".join(fv.strip() for fv in field_values[1:])
            attributes[field_name] = field_value

        page_content_box = cls.driver().find_element(
            By.XPATH, "//div[@class = 'notion-page-content']"
        )
        page_content = page_content_box.text

        title_edit = cls.driver().find_element(
            By.XPATH,
            "//div[@class='notion-selectable notion-page-block']/div[@contenteditable='true']",
        )
        title = title_edit.text
        title_edit.send_keys(Keys.ESCAPE)  # Get out of the edit flow!

        return ExtractedNotionRow(
            title=title, attributes=attributes, page_content=page_content
        )

    @classmethod
    def check_notion_row_exists(cls, title: str) -> bool:
        """Check that a Notion row exists in the current board."""
        cls.driver().implicitly_wait(0)

        try:
            for _ in range(1, 10):
                cls.driver().find_element(
                    By.XPATH,
                    f"//div[@data-block-id and contains(@class, 'notion-collection-item') and contains(., '{title}')]",
                )
                time.sleep(1)
                cls.driver().refresh()
            return True
        except (NoSuchElementException, TimeoutException):
            return False
        finally:
            cls.driver().implicitly_wait(cls._MAX_WAIT_TIME_SECONDS)

    @property
    def cache_path(self) -> Path:
        """The path to the integration tests cache."""
        if self._cache_path is None:
            raise Exception("No cache path")
        return self._cache_path

    @classmethod
    def driver(cls) -> WebDriver:
        """The selenium driver itself."""
        if cls._driver is None:
            raise Exception("No driver")
        return cls._driver

    @property
    def space_id(self) -> str:
        """The Notion space id of the standard testing space."""
        if self._space_id is None:
            raise Exception("No space id")
        return self._space_id

    @property
    def token_v2(self) -> str:
        """The Notion access token for the user and testing space."""
        if self._token_v2 is None:
            raise Exception("No token")
        return self._token_v2

    @property
    def notion_api_token(self) -> str:
        """The Notion API access token."""
        if self._notion_api_token is None:
            raise Exception("No API token")
        return self._notion_api_token


class JupiterIntegrationTestCase(JupiterBasicIntegrationTestCase):
    """A base class for Jupiter integration test cases which all work in a single workspace."""

    def setUp(self) -> None:
        """Set up a particular test."""
        if self._tmp_file is None:
            raise Exception("Missing temporary storage for Jupiter")
        if not self._tmp_file.is_file():
            self.jupiter(
                "init",
                "--name",
                "My Work",
                "--timezone",
                "Europe/Bucharest",
                "--notion-space-id",
                self.space_id,
                "--notion-token",
                self.token_v2,
                "--notion-api-token",
                self.notion_api_token,
                "--project-key",
                "work",
                "--project-name",
                "Work",
            )
            self.jupiter(
                "project-create", "--project", "personal", "--name", "Personal"
            )
        else:
            self.jupiter(
                "test-helper-clear-all",
                "--workspace-name",
                "My Work",
                "--workspace-timezone",
                "Europe/Bucharest",
                "--default-project",
                "work",
            )


def extract_id_from_show_out(out_str: str, match_hint: str) -> str:
    """Extract an entity id from show output."""
    pattern = re.compile(r"id=(\d+) " + match_hint)
    match = pattern.search(out_str)
    if not match:
        raise AssertionError(f"Output from show command is wrong:\n{out_str}")
    task_id = match.group(1)
    return task_id
