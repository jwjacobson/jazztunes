# Tests of browse.html

from playwright.sync_api import expect


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

    expect(page.locator("#id_knowledge")).to_be_visible()

    page.get_by_role("link", name="jazztunes").click()

    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)

    expect(first_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )
    expect(first_row.locator("td").nth(9)).to_contain_text("know")


def test_browse_page_take_and_set(small_rep_admin, single_tune_page):
    page = single_tune_page

    page.get_by_role("link", name="Browse").click()
    page.get_by_role("row", name="A Flower is a Lovesome Thing").get_by_role(
        "button"
    ).click()
    page.locator("#id_knowledge").select_option("learning")
    page.get_by_role("button", name="Set").click()

    expect(page.locator("#id_knowledge")).to_be_hidden()

    page.get_by_role("link", name="jazztunes").click()
    all_rows = page.locator("#rep-table tbody tr")
    first_row = all_rows.nth(0)
    expect(first_row.locator("td").nth(0)).to_contain_text(
        "A Flower is a Lovesome Thing"
    )
    expect(first_row.locator("td").nth(9)).to_contain_text("learning")


def test_browse_page_search_basic(small_rep_admin, single_tune_page):
    page = single_tune_page

    page.get_by_role("link", name="Browse").click()
    full_rep = page.locator("#public-table tbody").text_content()
    page.locator("#id_search_term").click()
    page.locator("#id_search_term").fill("love")
    page.get_by_role("button", name="Search").click()
    expect(page.locator("#public-table tbody")).not_to_have_text(full_rep)
    all_rows = page.locator("#public-table tbody tr")
    row_count = all_rows.count()

    for i in range(row_count):
        row = all_rows.nth(i)
        title = row.locator("td").nth(0).text_content()
        assert "love" in title.lower()
