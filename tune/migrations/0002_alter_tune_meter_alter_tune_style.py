# Generated by Django 5.0.4 on 2024-06-20 15:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tune", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tune",
            name="meter",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[
                    (3, "3"),
                    (4, "4"),
                    (5, "5"),
                    (6, "6"),
                    (7, "7"),
                    (0, "irregular"),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tune",
            name="style",
            field=models.CharField(
                blank=True,
                choices=[("standard", "standard"), ("jazz", "jazz")],
                max_length=15,
            ),
        ),
    ]
