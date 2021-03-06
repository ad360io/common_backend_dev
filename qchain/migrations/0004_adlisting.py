# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-09-05 17:05
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qchain', '0003_auto_20170813_1720'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdListing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('currency', models.CharField(choices=[(b'eqc', b'EQC'), (b'xqc', b'XQC')], max_length=4)),
                ('asking_rate', models.DecimalField(decimal_places=8, max_digits=12, validators=[django.core.validators.MinValueValidator(0), django.core.validators.DecimalValidator(12, 8)])),
                ('ask_date_from', models.DateField()),
                ('ask_date_to', models.DateField()),
                ('msg', models.CharField(max_length=140)),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qchain.Ad')),
            ],
        ),
    ]
