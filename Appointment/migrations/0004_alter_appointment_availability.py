# Generated by Django 5.1.5 on 2025-05-29 21:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0003_alter_appointment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='availability',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Appointment.availability'),
        ),
    ]
