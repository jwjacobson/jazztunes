import re

from playwright.sync_api import Page, expect
import pytest

from .constants import DOMAIN, LOGIN_SUFFIX, LOGIN_URL, USERNAME, PASSWORD


def test_login_redirect(page: Page):
    page.goto(DOMAIN)
    redirect_url = DOMAIN + LOGIN_SUFFIX
    assert page.url == redirect_url


def test_login_title(page: Page):
    page.goto(LOGIN_URL)
    expect(page).to_have_title(re.compile("Welcome to Jazztunes!"))


@pytest.mark.skip(reason="Tries to create an existing user")
def test_signup_from_homepage(page: Page):
    page.goto(LOGIN_URL)
    page.get_by_role("link", name="Sign up", exact=True).click()
    expect(page).to_have_title(re.compile("Sign up"))
    page.get_by_role("textbox", name="Username:").fill("user")
    page.get_by_role("textbox", name="Password:").fill("password")
    page.get_by_role("textbox", name="Password (again):").fill("password")
    page.get_by_role("button", name="Sign up").click()
    expect(page).to_have_title(re.compile("Home"))


def test_login_success(page: Page):
    page.goto(LOGIN_URL)
    page.get_by_role("textbox", name="Username:").click()
    page.get_by_role("textbox", name="Username:").fill(USERNAME)
    page.get_by_role("textbox", name="Password:").click()
    page.get_by_role("textbox", name="Password:").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page).to_have_title(re.compile("Home"))
    result = page.text_content("#rep_id")
    assert USERNAME in result
