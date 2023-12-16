from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import RepertoireTune


@receiver(pre_save, sender=RepertoireTune)
def start_learning(sender, instance, **kwargs):
    if instance.knowledge == "learning":
        instance.started_learning = timezone.now()
