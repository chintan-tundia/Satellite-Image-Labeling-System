# Generated by Django 2.2.1 on 2019-08-22 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gmapv2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marathi_name', models.CharField(max_length=100)),
                ('english_name', models.CharField(max_length=100)),
            ],
        ),
    ]