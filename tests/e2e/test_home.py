# Tests of home.html

from django.utils import timezone
from playwright.sync_api import expect
import pytest

from .constants import (
    SINGLE_TUNE_TITLE,
    DATE_DISPLAY_FORMAT,
    HomeColumns
)


@pytest.mark.django_db
def test_play_single_tune(single_tune_page):
    page = single_tune_page

    tune_row = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    tune_row.get_by_role("button", name="Play").click()

    today_string = timezone.now().date().strftime(DATE_DISPLAY_FORMAT)
    expect(tune_row.locator("td").nth(HomeColumns.LAST_PLAYED)).to_contain_text(today_string)


@pytest.mark.django_db
def test_delete_single_tune(single_tune_page):
    page = single_tune_page
    row_to_delete = page.locator("tr").filter(has_text=SINGLE_TUNE_TITLE)
    row_to_delete.get_by_role("button", name="Delete").click()

    expect(page.locator("text=Delete Yesterday's Tomorrows?")).to_be_visible()
    page.locator("#confirm-delete-button").click()

    result = page.text_content("#rep-table")
    expect(row_to_delete).to_be_hidden()


def test_home_search_basic(small_rep, logged_in_page):
    page = logged_in_page
    full_rep = page.locator("#rep-table tbody").text_content()
    page.locator("#id_search_term").click()
    page.locator("#id_search_term").fill("love")
    page.get_by_role("button", name="Search").click()
    expect(page.locator("#rep-table tbody")).not_to_have_text(full_rep)

    all_rows = page.locator("#rep-table tbody tr")
    row_count = all_rows.count()

    for i in range(row_count):
        row = all_rows.nth(i)
        title = row.locator("td").nth(0).text_content()
        assert "love" in title.lower()


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
    page.get_by_role("cell", name="Title").click()
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
    page.get_by_role("cell", name="Composer").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(1)).to_contain_text("Churchill")
    expect(last_row.locator("td").nth(1)).to_contain_text("Strayhorn")


def test_sort_composer_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Composer").click()
    page.get_by_role("cell", name="Composer").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(1)).to_contain_text("Strayhorn")
    expect(last_row.locator("td").nth(1)).to_contain_text("Churchill")


def test_sort_key_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Key: Activate to sort").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    # Coming on the Hudson has no key, so targeting by title
    expect(first_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")
    expect(last_row.locator("td").nth(2)).to_contain_text("F")


def test_sort_key_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Key: Activate to sort").click()
    page.get_by_role("cell", name="Key: Activate to invert").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(2)).to_contain_text("F")
    expect(last_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")


def test_sort_other_keys_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Other keys: Activate to sort").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    # Coming on the Hudson has no other keys, so targeting by title
    expect(first_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")
    expect(last_row.locator("td").nth(3)).to_contain_text("Db")


def test_sort_other_keys_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Other keys: Activate to sort").click()
    page.get_by_role("cell", name="Other keys: Activate to invert").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(3)).to_contain_text("Db")
    expect(last_row.locator("td").nth(0)).to_contain_text("Coming on the Hudson")


def test_sort_form_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Form").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(4)).to_contain_text("AABA")
    expect(last_row.locator("td").nth(4)).to_contain_text("ABAC")


def test_sort_form_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Form").click()
    page.get_by_role("cell", name="Form").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(4)).to_contain_text("ABAC")
    expect(last_row.locator("td").nth(4)).to_contain_text("AABA")


def test_sort_style_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Style").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(5)).to_contain_text("jazz")
    expect(last_row.locator("td").nth(5)).to_contain_text("standard")


def test_sort_style_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Style").click()
    page.get_by_role("cell", name="Style").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(5)).to_contain_text("standard")
    expect(last_row.locator("td").nth(5)).to_contain_text("jazz")


def test_sort_meter_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Meter").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(6)).to_contain_text("3")
    expect(last_row.locator("td").nth(6)).to_contain_text("4")


def test_sort_meter_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Meter").click()
    page.get_by_role("cell", name="Meter").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(6)).to_contain_text("4")
    expect(last_row.locator("td").nth(6)).to_contain_text("3")


def test_sort_year_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Year").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(7)).to_contain_text("1937")
    expect(last_row.locator("td").nth(7)).to_contain_text("1958")


def test_sort_year_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Year").click()
    page.get_by_role("cell", name="Year").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(7)).to_contain_text("1958")
    expect(last_row.locator("td").nth(7)).to_contain_text("1937")


def test_sort_knowledge_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Knowledge").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(9)).to_contain_text("don't know")
    expect(last_row.locator("td").nth(9)).to_contain_text("learning")


def test_sort_knowledge_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Knowledge").click()
    page.get_by_role("cell", name="Knowledge").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    last_row = all_rows.nth(-1)

    expect(first_row.locator("td").nth(9)).to_contain_text("learning")
    expect(last_row.locator("td").nth(9)).to_contain_text("don't know")


def test_sort_last_played_ascending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Last Played").click()

    rows = page.locator("#rep-table tbody tr")
    dates = [
        rows.nth(i).locator("td").nth(HomeColumns.LAST_PLAYED).inner_text()
        for i in range(rows.count())
    ]

    assert dates == sorted(dates)


def test_sort_last_played_descending(small_rep, logged_in_page):
    page = logged_in_page
    page.get_by_role("cell", name="Last Played").click()
    page.get_by_role("cell", name="Last Played").click()

    rows = page.locator("#rep-table tbody tr")
    dates = [
        rows.nth(i).locator("td").nth(HomeColumns.LAST_PLAYED).inner_text()
        for i in range(rows.count())
    ]

    assert dates == sorted(dates, reverse=True)

# TODO: test doublesorts
