import re

from django.utils import timezone
from playwright.sync_api import expect
import pytest

from .constants import (
    USERNAME,
    PASSWORD,
    SINGLE_TUNE_TITLE,
    SINGLE_TUNE_COMPOSER,
    SINGLE_TUNE_KEY,
    SINGLE_TUNE_OTHER_KEYS,
    SINGLE_TUNE_FORM,
    SINGLE_TUNE_STYLE,
    SINGLE_TUNE_METER,
    SINGLE_TUNE_YEAR,
    SINGLE_TUNE_KNOWLEDGE,
    SINGLE_TUNE_LAST_PLAYED_DISPLAY,
    DATE_DISPLAY_FORMAT,
)


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
def test_add_tune(single_tune_page):
    page = single_tune_page

    expect(page).to_have_title(re.compile("Home"))

    created_row = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    expect(created_row.locator("td").nth(0)).to_contain_text(SINGLE_TUNE_TITLE)
    expect(created_row.locator("td").nth(1)).to_contain_text(SINGLE_TUNE_COMPOSER)
    expect(created_row.locator("td").nth(2)).to_contain_text(SINGLE_TUNE_KEY)
    expect(created_row.locator("td").nth(3)).to_contain_text(SINGLE_TUNE_OTHER_KEYS)
    expect(created_row.locator("td").nth(4)).to_contain_text(SINGLE_TUNE_FORM)
    expect(created_row.locator("td").nth(5)).to_contain_text(SINGLE_TUNE_STYLE)
    expect(created_row.locator("td").nth(6)).to_contain_text(str(SINGLE_TUNE_METER))
    expect(created_row.locator("td").nth(7)).to_contain_text(SINGLE_TUNE_YEAR)
    # expect(created_row.locator("td").nth(8)).to_contain_text(SINGLE_TUNE_TAGS)
    expect(created_row.locator("td").nth(9)).to_contain_text(SINGLE_TUNE_KNOWLEDGE)
    expect(created_row.locator("td").nth(10)).to_contain_text(
        SINGLE_TUNE_LAST_PLAYED_DISPLAY
    )


@pytest.mark.django_db
def test_play_single_tune(single_tune_page):
    page = single_tune_page

    tune_row = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    tune_row.get_by_role("button", name="Play").click()

    today_string = timezone.now().date().strftime(DATE_DISPLAY_FORMAT)
    expect(tune_row.locator("td").nth(10)).to_contain_text(today_string)


@pytest.mark.django_db
def test_edit_single_tune(single_tune_page):
    page = single_tune_page
    row_to_edit = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    row_to_edit.get_by_role("button", name="Edit").click()
    page.locator('input[name="composer"]').fill("Sequeira")
    page.get_by_role("button", name="Save").click()

    edited_row = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    expect(edited_row.locator("td").nth(1)).to_contain_text("Sequeira")


@pytest.mark.django_db
def test_delete_single_tune(single_tune_page):
    page = single_tune_page
    row_to_delete = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    row_to_delete.get_by_role("button", name="Delete").click()

    expect(page.locator("text=Delete Yesterday's Tomorrows?")).to_be_visible()
    page.locator("#confirm-delete-button").click()

    result = page.text_content("#rep_id")
    assert SINGLE_TUNE_TITLE not in result
