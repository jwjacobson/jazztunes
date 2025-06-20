import re

from playwright.sync_api import expect
import pytest

from .constants import USERNAME, PASSWORD


def test_login_title(page, live_server):
    page.goto(live_server.url)
    expect(page).to_have_title(re.compile("Welcome to Jazztunes!"))


def test_signup_from_homepage(page, live_server):
    page.goto(live_server.url)
    page.get_by_role("link", name="Sign up", exact=True).click()
    expect(page).to_have_title(re.compile("Sign up"))
    page.get_by_role("textbox", name="Username:").fill(USERNAME)
    page.get_by_role("textbox", name="Password:").fill(PASSWORD)
    page.get_by_role("textbox", name="Password (again):").fill(PASSWORD)
    page.get_by_role("button", name="Sign up").click()
    expect(page).to_have_title(re.compile("Home"))
    result = page.text_content("#rep_id")
    assert USERNAME in result


def test_login_success(page, live_server, test_user):
    page.goto(live_server.url)
    page.get_by_role("textbox", name="Username:").click()
    page.get_by_role("textbox", name="Username:").fill(test_user.username)
    page.get_by_role("textbox", name="Password:").click()
    page.get_by_role("textbox", name="Password:").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()

    result = page.text_content("#rep_id")

    expect(page).to_have_title(re.compile("Home"))
    assert test_user.username in result


@pytest.mark.django_db
def test_add_tune(logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Add").click()
    page.locator('input[name="title"]').click()
    page.locator('input[name="title"]').fill("Yesterday's Tomorrows")
    page.locator('input[name="key"]').click()
    page.locator('input[name="composer"]').fill("Belderbos")
    page.locator('input[name="key"]').click()
    page.locator('input[name="key"]').fill("c")
    page.locator('input[name="other_keys"]').click()
    page.locator('input[name="other_keys"]').fill("A- F")
    page.locator('select[name="song_form"]').select_option("AABA")
    page.locator('select[name="style"]').select_option("standard")
    page.get_by_role("spinbutton").click()
    page.get_by_role("spinbutton").fill("2024")
    page.locator("#id_last_played").fill("2025-06-17")
    page.locator("#id_knowledge").select_option("learning")
    # page.get_by_role("checkbox", name="latin").check() TODO: create some tags in the test environment
    page.get_by_role("button", name="Add").click()

    result = page.text_content("#rep-table")

    expect(page).to_have_title(re.compile("Home"))
    assert "Tomorrows" in result
    assert "Belderbos" in result
    assert "A-" in result
    assert "AABA" in result
    assert "standard" in result
    assert "2024" in result
    assert "June 17" in result
    assert "learning" in result
