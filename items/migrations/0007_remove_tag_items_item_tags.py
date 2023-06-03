# Generated by Django 4.2.1 on 2023-06-02 22:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("items", "0006_alter_download_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tag",
            name="items",
        ),
        migrations.AddField(
            model_name="item",
            name="tags",
            field=models.ManyToManyField(to="items.tag"),
        ),
    ]
