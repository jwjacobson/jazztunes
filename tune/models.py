from django.db import models

class Tune(models.Model):
    """
    The Tune is the heart of this app; each tune is one song that can be added to a user's repertoire and should contain all relevant musical information.
    """
    METERS = [
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (0, 'irregular')
    ]

    STYLES = [
        ('standard', 'standard'),
        ('jazz', 'jazz')
    ]

    FORMS = [
        ('aaba', 'AABA'),
        ('abac', 'ABAC'),
        ('aba', 'ABA'),
        ('abab', 'ABAB'),
        ('blues', 'blues'),
        ('irregular', 'irregular'),
    ]

    title = models.CharField(max_length=100, unique=True)
    composer = models.CharField(max_length=30, blank=True)
    key = models.CharField(max_length=10, blank=True, help_text='The main key of the tune')
    other_keys = models.CharField(max_length=20, blank=True, help_text='Key(s) a tune modulates to in addition to the main key')
    song_form = models.CharField(choices=FORMS, max_length=15, blank=True)
    style = models.CharField(choices=STYLES, max_length=15, blank=True)
    meter = models.PositiveSmallIntegerField(choices=METERS, blank=True)
    year = models.PositiveSmallIntegerField(blank=True)
    # players = models.ForeignKey(Player, related_name='tunes', on_delete=models.CASCADE) # This field defines which players (users) have the tune in their repertoire
    
    @property
    def decade(self):
        """
        Calculate the decade of composition based on the year of composition.
        """
        decade = f'{self.year[2]}0s' 
        return decade

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'Tune {self.id} | {self.title}'
