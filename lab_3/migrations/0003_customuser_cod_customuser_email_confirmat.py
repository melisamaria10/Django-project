# Generated by Django 5.1.2 on 2024-12-09 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_3', '0002_alter_customuser_data_nasterii_alter_customuser_gen'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cod',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='email_confirmat',
            field=models.BooleanField(default=False),
        ),
    ]
