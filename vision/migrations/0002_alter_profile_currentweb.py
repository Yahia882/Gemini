# Generated by Django 5.0.7 on 2024-08-09 11:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vision', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='currentWeb',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vision.webapp'),
        ),
    ]
