# Generated by Django 3.2.16 on 2023-12-25 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_auto_20231225_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatuser',
            name='e_mail',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='chatuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='chatuser',
            name='phone_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
