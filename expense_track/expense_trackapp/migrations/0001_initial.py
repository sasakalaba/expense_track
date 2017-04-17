# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-17 19:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import expense_trackapp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=expense_trackapp.models.get_current_time)),
                ('time', models.TimeField(default=expense_trackapp.models.get_current_time)),
                ('description', models.CharField(blank=True, default=b'', max_length=1024, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('comment', models.CharField(blank=True, default=b'', max_length=1024, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date', 'amount'],
            },
        ),
    ]
