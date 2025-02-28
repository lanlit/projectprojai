# Generated by Django 5.1.5 on 2025-02-04 09:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MyApp", "0002_diary_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="catprofile",
            name="catprofile_image",
            field=models.ImageField(
                blank=True, null=True, upload_to="catprofile_images/"
            ),
        ),
        migrations.AlterField(
            model_name="catprofile",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="catprofile",
            name="owner",
            field=models.ForeignKey(
                default=14,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
