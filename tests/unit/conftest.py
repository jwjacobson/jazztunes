import pytest
from django.contrib.auth import get_user_model


@pytest.fixture()
def tune_set(db, client, create_tune_set_for_user):
    """Unit test tune set with its own user"""
    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    return create_tune_set_for_user(user)
