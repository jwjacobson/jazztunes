import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from tune.models import Tune

@pytest.mark.django_db
def test_new_tune(client):

    user = get_user_model().objects.create_user(username='testuser', password='12345')
    client.force_login(user)
    response = client.get(reverse('tune:tune_new'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].instance.pk is None

    # submit a form using TuneForm
    title = 'test title'
    composer = 'test composer'
    key = 'C'
    other_keys = ''
    song_form = 'aaba'
    style = 'standard'
    meter = 4
    year = 2023
    players = user
    now = timezone.now()

    response = client.post(reverse('tune:tune_new'),
                            {
                                'title': title,
                                'composer': composer,
                                'key': key,
                                'other_keys': other_keys,
                                'song_form': song_form,
                                'style': style,
                                'meter': meter,
                                'year': year,
                                'players': players,
                            })
    assert response.status_code == 302
    assert response.url == '/'
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


# write a test for a deleted tune
@pytest.mark.django_db
def test_delete_tune(client):

    user = get_user_model().objects.create_user(username='testuser', password='12345')
    client.force_login(user)
    response = client.get(reverse('tune:tune_new'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].instance.pk is None

    # submit a form using TuneForm
    title = 'test title'
    composer = 'test composer'
    key = 'C'
    other_keys = ''
    song_form = 'aaba'
    style = 'standard'
    meter = 4
    year = 2023
    players = user

    response = client.post(reverse('tune:tune_new'),
                            {
                                'title': title,
                                'composer': composer,
                                'key': key,
                                'other_keys': other_keys,
                                'song_form': song_form,
                                'style': style,
                                'meter': meter,
                                'year': year,
                                'players': players,
                            })
    assert response.status_code == 302
    assert response.url == '/'
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

    response = client.get(reverse('tune:tune_delete', kwargs={'pk': tune.pk}))
    assert response.status_code == 200

    response = client.post(reverse('tune:tune_delete', kwargs={'pk': tune.pk}))
    assert response.status_code == 302
    assert response.url == '/'
    with pytest.raises(Tune.DoesNotExist):
        Tune.objects.get(title=title)
