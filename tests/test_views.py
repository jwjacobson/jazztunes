import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from tune.models import Tune


@pytest.mark.django_db
def test_new_tune(client):
    user = get_user_model().objects.create_user(username="testuser", password="12345")
    client.force_login(user)
    response = client.get(reverse("tune:tune_new"))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].instance.pk is None

    # submit a form using TuneForm
    title = "test title"
    composer = "test composer"
    key = "C"
    other_keys = ""
    song_form = "aaba"
    style = "standard"
    meter = 4
    year = 2023
    players = user
    now = timezone.now()

    response = client.post(
        reverse("tune:tune_new"),
        {
            "title": title,
            "composer": composer,
            "key": key,
            "other_keys": other_keys,
            "song_form": song_form,
            "style": style,
            "meter": meter,
            "year": year,
            "players": players,
        },
    )
    assert response.status_code == 302
    assert response.url == "/"
    tune = Tune.objects.get(title=title)
    assert tune.title == title
    assert tune.composer == composer
    assert tune.key == key
    assert tune.other_keys == other_keys
    assert tune.song_form == song_form
    assert tune.style == style
    assert tune.meter == meter
    assert tune.year == year
    assert tune.players.first() == players
    assert tune.created_at >= now


@pytest.mark.django_db
def test_delete_tune(client):
    user = get_user_model().objects.create_user(username="testuser", password="12345")
    client.force_login(user)
    response = client.get(reverse("tune:tune_new"))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].instance.pk is None

    # submit a form using TuneForm
    title = "test title"
    composer = "test composer"
    key = "C"
    other_keys = ""
    song_form = "aaba"
    style = "standard"
    meter = 4
    year = 2023
    players = user

    response = client.post(
        reverse("tune:tune_new"),
        {
            "title": title,
            "composer": composer,
            "key": key,
            "other_keys": other_keys,
            "song_form": song_form,
            "style": style,
            "meter": meter,
            "year": year,
            "players": players,
        },
    )
    assert response.status_code == 302
    assert response.url == "/"
    tune = Tune.objects.get(title=title)
    assert tune.title == title
    assert tune.composer == composer
    assert tune.key == key
    assert tune.other_keys == other_keys
    assert tune.song_form == song_form
    assert tune.style == style
    assert tune.meter == meter
    assert tune.year == year
    assert tune.players.first() == players

    response = client.get(reverse("tune:tune_delete", kwargs={"pk": tune.pk}))
    assert response.status_code == 200

    response = client.post(reverse("tune:tune_delete", kwargs={"pk": tune.pk}))
    assert response.status_code == 302
    assert response.url == "/"
    with pytest.raises(Tune.DoesNotExist):
        Tune.objects.get(title=title)


# shelving this for now
# @pytest.mark.django_db
# def test_edit_tune(client):
#     # Create a user
#     user = get_user_model().objects.create_user(username="testuser", password="12345")
#     client.force_login(user)

#     # Create a Tune object to edit
#     original_title = "original title"
#     original_composer = "original composer"
#     original_key = "C"
#     original_other_keys = ""
#     original_song_form = "aaba"
#     original_style = "standard"
#     original_meter = 4
#     original_year = 2023
#     original_players = user

#     response = client.post(
#         reverse("tune:tune_new"),
#         {
#             "title": original_title,
#             "composer": original_composer,
#             "key": original_key,
#             "other_keys": original_other_keys,
#             "song_form": original_song_form,
#             "style": original_style,
#             "meter": original_meter,
#             "year": original_year,
#             "players": original_players,
#         },
#     )

#     breakpoint()

#     # Ensure the original Tune object exists
#     assert Tune.objects.filter(title=original_title).exists()

#     # Get the edit form for the Tune
#     response = client.get(reverse("tune:tune_edit", kwargs={"pk": original_tune.pk}))
#     assert response.status_code == 200
#     assert "form" in response.context
#     assert response.context["form"].instance.pk == original_tune.pk

#     # Update the Tune object with new data
#     new_title = "new title"
#     new_composer = "new composer"
#     new_key = "D"
#     new_other_keys = "F"
#     new_song_form = "abac"
#     new_style = "jazz"
#     new_meter = 3
#     new_year = 2024

#     response = client.post(
#         reverse("tune:tune_edit", kwargs={"pk": original_tune.pk}),
#         {
#             "title": new_title,
#             "composer": new_composer,
#             "key": new_key,
#             "other_keys": new_other_keys,
#             "song_form": new_song_form,
#             "style": new_style,
#             "meter": new_meter,
#             "year": new_year,
#             "players": original_players.id,  # Use the user ID for the players field
#         },
#     )

#     # Ensure the form submission was successful
#     assert response.status_code == 302
#     assert response.url == "/"

#     # Retrieve the updated Tune object from the database
#     updated_tune = Tune.objects.get(pk=original_tune.pk)

#     # Verify that the Tune object has been updated with the new data
#     assert updated_tune.title == new_title
#     assert updated_tune.composer == new_composer
#     assert updated_tune.key == new_key
#     assert updated_tune.other_keys == new_other_keys
#     assert updated_tune.song_form == new_song_form
#     assert updated_tune.style == new_style
#     assert updated_tune.meter == new_meter
#     assert updated_tune.year == new_year
#     assert updated_tune.players == original_players
