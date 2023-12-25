# Generated by Django 3.2.16 on 2023-12-25 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatuser',
            name='e_mail',
            field=models.CharField(default='none', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chatuser',
            name='phone_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
