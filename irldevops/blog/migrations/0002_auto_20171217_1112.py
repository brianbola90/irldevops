# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-17 11:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['created'], 'verbose_name_plural': 'posts'},
        ),
    ]
