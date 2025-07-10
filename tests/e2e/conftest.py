import os

from django.contrib.auth.models import User
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
    SINGLE_TUNE_YEAR,
    SINGLE_TUNE_KNOWLEDGE,
    SINGLE_TUNE_LAST_PLAYED,
)

# Setting this value to allow async Playwright to run sync Django:
# "django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async."
# See https://docs.djangoproject.com/en/5.2/topics/async/#async-safety
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def test_user(transactional_db, is_admin=False):
    user = User.objects.create_user(
        username=USERNAME,
        password=PASSWORD,
    )

    return user


@pytest.fixture
def admin_user(transactional_db):
    """Create an admin user"""
    user = User.objects.create_user(
        username="admin_" + USERNAME, password=PASSWORD, is_staff=True
    )
    from django.conf import settings

    settings.ADMIN_USER_ID = user.id

    return user


@pytest.fixture()
def logged_in_page(page, test_user, live_server):
    page.goto(live_server.url)
    page.get_by_role("textbox", name="Username:").click()
    page.get_by_role("textbox", name="Username:").fill(test_user.username)
    page.get_by_role("textbox", name="Password:").click()
    page.get_by_role("textbox", name="Password:").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()

    yield page


@pytest.fixture()
def single_tune_page(logged_in_page, test_user, live_server):
    page = logged_in_page
    page.locator("#nav-add").click()
    page.locator('input[name="title"]').click()
    page.locator('input[name="title"]').fill(SINGLE_TUNE_TITLE)
    page.locator('input[name="key"]').click()
    page.locator('input[name="composer"]').fill(SINGLE_TUNE_COMPOSER)
    page.locator('input[name="key"]').click()
    page.locator('input[name="key"]').fill(SINGLE_TUNE_KEY)
    page.locator('input[name="other_keys"]').click()
    page.locator('input[name="other_keys"]').fill(SINGLE_TUNE_OTHER_KEYS)
    page.locator('select[name="song_form"]').select_option(SINGLE_TUNE_FORM)
    page.locator('select[name="style"]').select_option(SINGLE_TUNE_STYLE)
    page.get_by_role("spinbutton").click()
    page.get_by_role("spinbutton").fill(SINGLE_TUNE_YEAR)
    page.locator("#id_last_played").fill(SINGLE_TUNE_LAST_PLAYED)
    page.locator("#id_knowledge").select_option(SINGLE_TUNE_KNOWLEDGE)
    # page.get_by_role("checkbox", name="latin").check() TODO: create some tags in the test environment
    page.locator("#add-button").click()

    yield page


@pytest.fixture()
def small_rep(test_user, create_tune_set_for_user):
    """Create a user with a repertoire of ten real tunes"""
    create_tune_set_for_user(test_user)
    return test_user


@pytest.fixture()
def small_rep_admin(admin_user, create_tune_set_for_user):
    """Create an admin user with a repertoire of ten real tunes"""
    result = create_tune_set_for_user(admin_user, is_admin=True)
    return result
