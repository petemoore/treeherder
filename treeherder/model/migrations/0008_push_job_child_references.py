# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-10 17:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0007_add_performance_data_expiry_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='push',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='model.Push'),
        ),
        migrations.AlterField(
            model_name='jobdetail',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_details', to='model.Job'),
        ),
    ]