# Generated by Django 3.2.16 on 2023-12-18 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_auto_20231218_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='aianswer',
            name='ai_prefix',
            field=models.TextField(default='Guru'),
            preserve_default=False,
        ),
    ]
