# Tests of play.html

from playwright.sync_api import expect


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
