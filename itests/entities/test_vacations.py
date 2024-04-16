"""Tests about vacations."""
import time

from playwright.sync_api import Page, expect


def test_vacation_create(page: Page) -> None:
    page.goto("/workspace/vacations")
    page.locator("#trunk-new-leaf-entity").click()
    page.locator('input[name="name"]').fill("First Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-10")
    page.locator('input[name="endDate"]').fill("2024-12-15")

    page.locator("#vacation-create").click()

    page.wait_for_url("/workspace/vacations/*")

    expect(page.locator('input[name="name"]')).to_have_value("First Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-10")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-15")


def test_vacation_update(page: Page) -> None:
    page.goto("/workspace/vacations")
    page.locator("#trunk-new-leaf-entity").click()
    page.locator('input[name="name"]').fill("First Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-10")
    page.locator('input[name="endDate"]').fill("2024-12-15")

    page.locator("#vacation-create").click()

    page.wait_for_url("/workspace/vacations/*")
    page.wait_for_selector("#leaf-panel")

    page.locator('input[name="name"]').fill("Updated Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-11")
    page.locator('input[name="endDate"]').fill("2024-12-16")

    page.locator("#vacation-update").click()

    page.wait_for_url("/workspace/vacations/*")
    page.wait_for_selector("#leaf-panel")

    expect(page.locator('input[name="name"]')).to_have_value("Updated Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-11")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-16")

    page.reload()
    page.wait_for_selector("#leaf-panel")

    expect(page.locator('input[name="name"]')).to_have_value("Updated Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-11")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-16")


def test_vacation_create_note(page: Page) -> None:
    page.goto("/workspace/vacations")
    page.locator("#trunk-new-leaf-entity").click()
    page.locator('input[name="name"]').fill("First Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-10")
    page.locator('input[name="endDate"]').fill("2024-12-15")

    page.locator("#vacation-create").click()

    page.wait_for_url("/workspace/vacations/*")
    page.wait_for_selector("#leaf-panel")

    page.locator("#vacation-create-note").click()
    page.wait_for_selector("#entity-block-editor")

    page.locator('#editorjs div[contenteditable="true"]').first.fill("This is a note.")

    page.wait_for_url("/workspace/vacations/*")

    expect(page.locator('#editorjs div[contenteditable="true"]').first).to_contain_text(
        "This is a note."
    )
    time.sleep(1)  # Wait for the update to be saved.

    page.reload()

    page.wait_for_selector("#leaf-panel")

    expect(page.locator('#editorjs div[contenteditable="true"]').first).to_contain_text(
        "This is a note."
    )


def test_vacation_archive(page: Page) -> None:
    page.goto("/workspace/vacations")
    page.locator("#trunk-new-leaf-entity").click()
    page.locator('input[name="name"]').fill("First Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-10")
    page.locator('input[name="endDate"]').fill("2024-12-15")

    page.locator("#vacation-create").click()

    page.wait_for_url("/workspace/vacations/*")
    page.wait_for_selector("#leaf-panel")

    page.locator("#leaf-entity-archive").click()

    expect(page.locator('input[name="name"]')).not_to_be_disabled()
    expect(page.locator('input[name="startDate"]')).not_to_be_disabled()
    expect(page.locator('input[name="endDate"]')).not_to_be_disabled()

    expect(page.locator("#vacation-update")).to_be_disabled()
    expect(page.locator("#vacation-create-note")).to_be_disabled()
    expect(page.locator("#leaf-entity-archive")).to_be_disabled()
