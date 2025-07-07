import re

from playwright.sync_api import expect


def test_authenticated_titles(small_rep, small_rep_admin, logged_in_page, live_server):
    page = logged_in_page

    expect(page).to_have_title(re.compile("Home"))

    row_to_edit = page.locator("tr").filter(has_text="Flower")

    row_to_edit.get_by_role("button", name="Edit").click()

    expect(page).to_have_title(re.compile("Edit tune"))

    page.get_by_role("link", name="Add").click()

    expect(page).to_have_title(re.compile("New tune"))

    page.get_by_role("link", name="Play").click()

    expect(page).to_have_title(re.compile("Play"))

    page.get_by_role("link", name="Browse").click()

    expect(page).to_have_title(re.compile("Public Tunes"))

    page.get_by_role("link", name="Log Out").click()

    expect(page).to_have_title(re.compile("Sign Out"))

    page.get_by_role("link", name="jazztunes").click()

    expect(page).to_have_title(re.compile("Home"))

    with page.expect_popup() as page1_info:
        page.get_by_role("link", name="Manual").click()

    page1 = page1_info.value

    expect(page1).to_have_title(re.compile("Jazztunes Docs"))
