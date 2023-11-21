from django.db import models

class Tune(models.Model):
    """
    The Tune is the heart of this app; it contains
    """
    title = models.CharField(max_length=100, unique=True)
    composer = models.CharField(max_length=30, blank=True)
    key = models.CharField(max_length=10, blank=True)           # The main key of a tune
    other_keys = models.CharField(max_length=20, blank=True)    # Key(s) a tune modulates to in addition to the main key
    song_form = models.CharField(max_length=20, blank=True)
    style = models.CharField(max_length=20, blank=True)
    meter = models.CharField(max_length=10, blank=True)
    year = models.CharField(max_length=10, blank=True)
    # decade = models.CharField(max_length==10, blank=True)       # I would like the decade field to be automatically calculated from year;
                                                                # it looks like
    # players = models.ForeignKey(Player, related_name='tunes', on_delete=models.CASCADE) # This field defines which players (users) have the tune in their repertoire

    # def decade(self):
    #     return year[2:] + s

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'Tune {self.id} | {self.title}'
