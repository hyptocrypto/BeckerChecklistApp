# Generated by Django 4.1.7 on 2023-04-04 20:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checklist", "0002_alter_startedjob_client_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="startedjob",
            name="client_name",
            field=models.CharField(default="", max_length=200),
        ),
    ]
