# Generated by Django 4.2.7 on 2023-12-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tune", "0023_alter_tune_song_form"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tune",
            name="meter",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (0, "irregular")],
                default=4,
                null=True,
            ),
        ),
    ]