# Generated by Django 4.2.7 on 2023-12-05 03:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tune", "0014_remove_tune_players_tune_created_by_repertoiretune"),
    ]

    operations = [
        migrations.RenameField(
            model_name="repertoiretune",
            old_name="tune",
            new_name="rep_tune",
        ),
    ]
