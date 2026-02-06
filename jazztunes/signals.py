# jazztunes -- A jazz repertoire management app
# Copyright (C) 2024 Jeff Jacobson <jeffjacobsonhimself@gmail.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import RepertoireTune


@receiver(pre_save, sender=RepertoireTune)
def start_learning(sender, instance, **kwargs):
    if instance.knowledge == "learning":
        instance.started_learning = timezone.now()
