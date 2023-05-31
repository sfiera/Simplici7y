# Generated by Django 4.2.1 on 2023-05-30 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("items", "0002_tag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="tc",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="items.item",
            ),
        ),
    ]