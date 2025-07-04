import re

from playwright.sync_api import expect

from .constants import (
    USERNAME,
    PASSWORD,
)


def test_login_titles(page, live_server):
    page.goto(live_server.url)
    expect(page).to_have_title(re.compile("Welcome to Jazztunes!"))
    page.get_by_role("link", name="Sign up", exact=True).click()
    expect(page).to_have_title(re.compile("Sign up"))
    page.goto(live_server.url)
    page.get_by_role("link", name="Forgot your password?").click()
    expect(page).to_have_title(re.compile("Password Reset"))


def test_signup_from_homepage(page, live_server):
    page.goto(live_server.url)

    page.get_by_role("link", name="Sign up", exact=True).click()
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
