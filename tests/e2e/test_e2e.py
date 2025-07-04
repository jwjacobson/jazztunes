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


def test_login_titles(page, live_server):
    page.goto(live_server.url)
    expect(page).to_have_title(re.compile("Welcome to Jazztunes!"))
    page.get_by_role("link", name="Sign up", exact=True).click()
    expect(page).to_have_title(re.compile("Sign up"))
    page.goto(live_server.url)
    page.get_by_role("link", name="Forgot your password?").click()
    expect(page).to_have_title(re.compile("Password Reset"))


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


@pytest.mark.django_db
def test_add_tune(single_tune_page):
    page = single_tune_page

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
    page.locator('input[name="title"]').fill("Tomorrow's Yesterdays")
    page.locator('input[name="composer"]').fill("Sequeira")
    page.get_by_role("button", name="Save").click()

    edited_row = page.locator("tr").filter(has_text="Tomorrow's Yesterdays")
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


# TODO: parametrize the sorting tests
def test_sort_default_title_ascending(small_rep, logged_in_page):
    page = logged_in_page
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )
    expect(last_row.locator("td").nth(0)).to_contain_text("Someday My Prince Will Come")


def test_sort_title_descending_click_cell(small_rep, logged_in_page):
    page = logged_in_page
    # Sort by clicking the header cell
    page.get_by_role("cell", name="Title: Activate to invert").locator("span").nth(
        1
    ).click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(0)).to_contain_text(
        "Someday My Prince Will Come"
    )
    expect(last_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )


def test_sort_title_descending_click_text(small_rep, logged_in_page):
    page = logged_in_page
    # Sort by clicking the header text
    page.get_by_role("button", name="Title").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(0)).to_contain_text(
        "Someday My Prince Will Come"
    )
    expect(last_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )


def test_sort_composer_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Composer").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(1)).to_contain_text("Churchill")
    expect(last_row.locator("td").nth(1)).to_contain_text("Strayhorn")


def test_sort_composer_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Composer").click()
    page.get_by_role("button", name="Composer").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(1)).to_contain_text("Strayhorn")
    expect(last_row.locator("td").nth(1)).to_contain_text("Churchill")


def test_sort_key_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Key", exact=True).click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    # Coming on the Hudson has no key, so targeting by title
    expect(first_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")
    expect(last_row.locator("td").nth(2)).to_contain_text("F")


def test_sort_key_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Key", exact=True).click()
    page.get_by_role("button", name="Key", exact=True).click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(2)).to_contain_text("F")
    expect(last_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")


def test_sort_other_keys_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Other keys").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    # Coming on the Hudson has no other keys, so targeting by title
    expect(first_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")
    expect(last_row.locator("td").nth(3)).to_contain_text("Db")


def test_sort_other_keys_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Other keys", exact=True).click()
    page.get_by_role("button", name="Other keys", exact=True).click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(3)).to_contain_text("Db")
    expect(last_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")


def test_sort_form_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Form").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(4)).to_contain_text("AABA")
    expect(last_row.locator("td").nth(4)).to_contain_text("ABAC")


def test_sort_form_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Form").click()
    page.get_by_role("button", name="Form").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(4)).to_contain_text("ABAC")
    expect(last_row.locator("td").nth(4)).to_contain_text("AABA")


def test_sort_style_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Style").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(5)).to_contain_text("jazz")
    expect(last_row.locator("td").nth(5)).to_contain_text("standard")


def test_sort_style_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Style").click()
    page.get_by_role("button", name="Style").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(5)).to_contain_text("standard")
    expect(last_row.locator("td").nth(5)).to_contain_text("jazz")


def test_sort_meter_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Meter").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(6)).to_contain_text("3")
    expect(last_row.locator("td").nth(6)).to_contain_text("4")


def test_sort_meter_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Meter").click()
    page.get_by_role("button", name="Meter").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(6)).to_contain_text("4")
    expect(last_row.locator("td").nth(6)).to_contain_text("3")


def test_sort_year_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Year").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(7)).to_contain_text("1937")
    expect(last_row.locator("td").nth(7)).to_contain_text("1958")


def test_sort_year_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Year").click()
    page.get_by_role("button", name="Year").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(7)).to_contain_text("1958")
    expect(last_row.locator("td").nth(7)).to_contain_text("1937")


def test_sort_knowledge_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Knowledge").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(9)).to_contain_text("don't know")
    expect(last_row.locator("td").nth(9)).to_contain_text("learning")


def test_sort_knowledge_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Knowledge").click()
    page.get_by_role("button", name="Knowledge").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(9)).to_contain_text("learning")
    expect(last_row.locator("td").nth(9)).to_contain_text("don't know")


def test_sort_last_played_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Last Played").click()

    date_cells = page.locator("#rep-table tbody tr td[id^='last-played-']")
    timestamps = [
        int(date_cells.nth(i).get_attribute("data-order"))
        for i in range(date_cells.count())
    ]

    assert timestamps == sorted(timestamps)


def test_sort_last_played_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("button", name="Last Played").click()
    page.get_by_role("button", name="Last Played").click()

    date_cells = page.locator("#rep-table tbody tr td[id^='last-played-']")
    timestamps = [
        int(date_cells.nth(i).get_attribute("data-order"))
        for i in range(date_cells.count())
    ]

    assert timestamps == sorted(timestamps, reverse=True)


# TODO: test doublesorts


def test_play_page_basic(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.get_by_role("button", name="Search").click()
    page.wait_for_selector("#playTuneWrapper")

    expect(page.locator("#playTuneWrapper")).to_be_visible()
    expect(page.locator("#playTuneWrapper")).to_contain_text("You should play...")
    expect(page.get_by_role("button", name="Play")).to_be_visible()
    expect(page.get_by_role("button", name="No thanks...")).to_be_visible()
    expect(page.locator("#key-suggestion")).not_to_be_visible()


def test_play_page_search(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.locator("#id_search_term").click()
    page.locator("#id_search_term").fill("flower")
    page.get_by_role("button", name="Search").click()
    page.wait_for_selector("#playTuneWrapper")

    expect(page.locator("#playTuneWrapper")).to_contain_text(
        "A Flower is a Lovesome Thing"
    )
    expect(page.locator("#key-suggestion")).not_to_be_visible()


def test_play_page_search_suggest_key(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.locator("#id_suggest_key").check()
    page.get_by_role("button", name="Search").click()
    page.wait_for_selector("#playTuneWrapper")

    expect(page.locator("#key-suggestion")).to_be_visible()
    expect(page.locator("#key-suggestion")).to_contain_text("in")


def test_play_page_search_accept(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.get_by_role("button", name="Search").click()
    page.wait_for_selector("#playTuneWrapper")
    page.get_by_role("button", name="Play").click()
    page.wait_for_function("() => document.querySelector('button[disabled]')")

    expect(page.get_by_role("button", name="Play")).to_be_disabled()
    expect(page.get_by_role("button", name="No thanks...")).to_have_count(0)
    expect(page.get_by_role("button", name="One more!")).to_be_visible()


def test_play_page_search_accept_accept(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.get_by_role("button", name="Search").click()
    page.wait_for_selector("#playTuneWrapper")
    page.get_by_role("button", name="Play").click()
    page.wait_for_function("() => document.querySelector('button[disabled]')")
    page.get_by_role("button", name="One more!").click()

    expect(page.get_by_role("button", name="Play")).to_be_visible()
    expect(page.get_by_role("button", name="No thanks...")).to_be_visible()


def test_play_page_search_reject(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.get_by_role("button", name="Search").click()
    page.wait_for_selector("#playTuneWrapper")
    first_title = page.locator("#selected-tune").text_content()
    page.get_by_role("button", name="No thanks...").click()

    expect(page.locator("#selected-tune")).not_to_have_text(first_title)
    expect(page.get_by_role("button", name="Play")).to_be_visible()
    expect(page.get_by_role("button", name="No thanks...")).to_be_visible()

    second_title = page.locator("#selected-tune").text_content()
    assert second_title != first_title


def test_play_page_search_no_results(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.locator("#id_search_term").click()
    page.locator("#id_search_term").fill("xzx")
    page.get_by_role("button", name="Search").click()

    expect(page.locator("#playTuneWrapper")).to_contain_text(
        "No more matching tunes..."
    )
    expect(page.locator("#playTuneWrapper")).to_contain_text("Try another search?")


def test_play_page_search_reject_no_results(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("link", name="Play").click()

    page.locator("#id_search_term").click()
    page.locator("#id_search_term").fill("flower")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("button", name="No thanks...").click()

    expect(page.locator("#playTuneWrapper")).to_contain_text(
        "No more matching tunes..."
    )
    expect(page.locator("#playTuneWrapper")).to_contain_text("Try another search?")


def test_browse_page_basic(small_rep_admin, single_tune_page):
    page = single_tune_page
    admin_tunes = small_rep_admin["tunes"]

    page.get_by_role("link", name="Browse").click()
    titles = {tune.tune.title for tune in admin_tunes}
    tune_table = page.text_content("#public-table")
    for title in titles:
        assert title in tune_table


def test_browse_page_take_no_set(small_rep_admin, single_tune_page):
    page = single_tune_page

    page.get_by_role("link", name="Browse").click()
    page.get_by_role("row", name="A Flower is a Lovesome Thing").get_by_role(
        "button"
    ).click()

    expect(page.locator("#id_last_played")).to_be_visible()
    expect(page.locator("#id_knowledge")).to_be_visible()

    page.get_by_role("link", name="jazztunes").click()

    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)

    expect(first_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )
    expect(first_row.locator("td").nth(9)).to_contain_text("know")
    expect(first_row.locator("td").nth(10)).to_be_empty()


def test_browse_page_take_and_set(small_rep_admin, single_tune_page):
    page = single_tune_page

    page.get_by_role("link", name="Browse").click()
    page.get_by_role("row", name="A Flower is a Lovesome Thing").get_by_role(
        "button"
    ).click()
    page.locator("#id_last_played").fill("2025-07-02")
    page.locator("#id_knowledge").select_option("learning")
    page.get_by_role("button", name="Set").click()

    expect(page.locator("#id_last_played")).to_be_hidden()
    expect(page.locator("#id_knowledge")).to_be_hidden()

    page.get_by_role("link", name="jazztunes").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    expect(first_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )
    expect(first_row.locator("td").nth(9)).to_contain_text("learning")
    expect(first_row.locator("td").nth(10)).to_contain_text("July 2")


@pytest.mark.skip(reason="Doesn't work yet")
def test_browse_page_search(small_rep_admin, single_tune_page):
    page = single_tune_page

    page.get_by_role("link", name="Browse").click()
    page.locator("#id_search_term").click()
    page.locator("#id_search_term").fill("love")
    page.get_by_role("button", name="Search").click()
    all_rows = page.locator("#public-table tbody tr")
    row_count = all_rows.count()
    breakpoint()

    for i in range(row_count):
        print(all_rows.nth(i))
