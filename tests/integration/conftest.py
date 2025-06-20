import os

from django.contrib.auth.models import User
import pytest

from .constants import USERNAME, PASSWORD

# Setting this value to avoid a crash: "django.core.exceptions.SynchronousOnlyOperation:
# You cannot call this from an async context - use a thread or sync_to_async."
# See https://github.com/microsoft/playwright-pytest/issues/29#issuecomment-731515676
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def test_user(transactional_db):
    user = User.objects.create_user(
        username=USERNAME,
        password=PASSWORD,
    )
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
