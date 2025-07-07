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
