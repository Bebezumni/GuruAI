# Generated by Django 3.2.16 on 2023-12-24 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_auto_20231222_1353'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('login', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('instruction', models.CharField(max_length=3000)),
            ],
        ),
    ]