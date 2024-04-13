import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev")
    expect(page).to_have_title(re.compile("Playwright"))
