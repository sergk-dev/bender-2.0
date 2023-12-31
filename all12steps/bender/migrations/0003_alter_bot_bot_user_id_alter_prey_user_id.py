# Generated by Django 4.2.2 on 2023-06-20 19:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bender", "0002_alter_prey_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bot",
            name="bot_user_id",
            field=models.BigIntegerField(default=0, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="prey",
            name="user_id",
            field=models.CharField(max_length=50),
        ),
    ]
