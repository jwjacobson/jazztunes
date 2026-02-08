# Tests of form.html


from playwright.sync_api import expect
import pytest

from .constants import (
    SINGLE_TUNE_TITLE,
    SINGLE_TUNE_COMPOSER,
    SINGLE_TUNE_KEY,
    SINGLE_TUNE_OTHER_KEYS,
    SINGLE_TUNE_FORM,
    SINGLE_TUNE_STYLE,
    SINGLE_TUNE_METER,
    SINGLE_TUNE_YEAR,
    SINGLE_TUNE_KNOWLEDGE,
)


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
