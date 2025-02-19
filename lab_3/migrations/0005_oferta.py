# Generated by Django 5.1.2 on 2024-12-15 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_3', '0004_promotie_vizualizare'),
    ]

    operations = [
        migrations.CreateModel(
            name='Oferta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nume', models.CharField(max_length=255)),
                ('descriere', models.TextField()),
            ],
            options={
                'permissions': [('vizualizeaza_oferta', 'Poate vizualiza oferta')],
            },
        ),
    ]
